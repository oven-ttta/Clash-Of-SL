import os

api_path = r"D:\Clash-Of-SL\Clash SL Server\WebAPI\API.cs"
with open(api_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add missing using statements
if "using MySql.Data.MySqlClient;" not in code:
    code = code.replace("using CSS.Helpers;", "using CSS.Helpers;\nusing MySql.Data.MySqlClient;\nusing CSS.Logic;\nusing System.Security.Cryptography;")

# Add new HTML loaders
html_loaders = """
        public static string HTML()
        {
            try
            {
                using (StreamReader sr = new StreamReader("WebAPI/HTML/Statistics.html"))
                {
                    return sr.ReadToEnd();
                }
            }
            catch (Exception)
            {
                return "File not Found";
            }
        }

        public static string GetHTML(string file)
        {
            try
            {
                using (StreamReader sr = new StreamReader("WebAPI/HTML/" + file))
                {
                    return sr.ReadToEnd();
                }
            }
            catch (Exception)
            {
                return "File not Found";
            }
        }
"""
code = code.replace("public static string HTML()\r\n        {\r\n            try\r\n            {\r\n                using (StreamReader sr = new StreamReader(\"WebAPI/HTML/Statistics.html\"))\r\n                {\r\n                    return sr.ReadToEnd();\r\n                }\r\n            }\r\n            catch (Exception)\r\n            {\r\n                return \"File not Found\";\r\n            }\r\n        }", html_loaders)

# Replace the handler loop
old_handler = """foreach (string _URL in Listener.Prefixes.ToList<string>())
                                    {
                                        if (ctx.Request.Url.ToString().Contains(_URL))
                                        {
                                            if (ctx.Request.Url.ToString().EndsWith("api/"))
                                            {
                                                byte[] responseBuf = Encoding.UTF8.GetBytes(GetjsonAPI());
                                                ctx.Response.ContentLength64 = responseBuf.Length;
                                                ctx.Response.OutputStream.Write(responseBuf, 0, responseBuf.Length);
                                                ctx.Response.OutputStream.Close();
                                            }
                                            else
                                            {
                                                byte[] responseBuf = Encoding.UTF8.GetBytes(GetStatisticHTML());
                                                ctx.Response.ContentLength64 = responseBuf.Length;
                                                ctx.Response.OutputStream.Write(responseBuf, 0, responseBuf.Length);
                                                ctx.Response.OutputStream.Close();
                                            }
                                        }
                                        else
                                        {
                                            byte[] responseBuf = Encoding.UTF8.GetBytes(GetStatisticHTML());
                                            ctx.Response.ContentLength64 = responseBuf.Length;
                                            ctx.Response.OutputStream.Write(responseBuf, 0, responseBuf.Length);
                                            ctx.Response.OutputStream.Close();
                                        }
                                    }"""

new_handler = """
                                    string path = ctx.Request.Url.AbsolutePath.ToLower();
                                    byte[] responseBuf;
                                    
                                    if (path == "/login")
                                    {
                                        responseBuf = Encoding.UTF8.GetBytes(GetHTML("login.html"));
                                    }
                                    else if (path == "/register")
                                    {
                                        responseBuf = Encoding.UTF8.GetBytes(GetHTML("register.html"));
                                    }
                                    else if (path == "/api/login" && ctx.Request.HttpMethod == "POST")
                                    {
                                        using (var reader = new StreamReader(ctx.Request.InputStream, ctx.Request.ContentEncoding))
                                        {
                                            string body = reader.ReadToEnd();
                                            responseBuf = Encoding.UTF8.GetBytes(HandleLoginApi(body));
                                        }
                                    }
                                    else if (path == "/api/register" && ctx.Request.HttpMethod == "POST")
                                    {
                                        using (var reader = new StreamReader(ctx.Request.InputStream, ctx.Request.ContentEncoding))
                                        {
                                            string body = reader.ReadToEnd();
                                            responseBuf = Encoding.UTF8.GetBytes(HandleRegisterApi(body));
                                        }
                                    }
                                    else if (path.EndsWith("api/"))
                                    {
                                        responseBuf = Encoding.UTF8.GetBytes(GetjsonAPI());
                                    }
                                    else
                                    {
                                        responseBuf = Encoding.UTF8.GetBytes(GetStatisticHTML());
                                    }

                                    ctx.Response.ContentLength64 = responseBuf.Length;
                                    ctx.Response.OutputStream.Write(responseBuf, 0, responseBuf.Length);
                                    ctx.Response.OutputStream.Close();
"""
code = code.replace(old_handler, new_handler)

api_methods = """
        public static string HandleLoginApi(string jsonBody)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(jsonBody);
                string username = data.username;
                string password = data.password;

                string connStr = "Server=" + Configuration.DatabaseHost + ";Port=" + Configuration.DatabasePort + ";Database=" + Configuration.DatabaseName + ";Uid=" + Configuration.DatabaseUser + ";Password=" + Configuration.DatabasePassword + ";";
                using (MySqlConnection conn = new MySqlConnection(connStr))
                {
                    conn.Open();
                    using (MySqlCommand cmd = new MySqlCommand("SELECT password_hash, player_id FROM users WHERE username = @u", conn))
                    {
                        cmd.Parameters.AddWithValue("@u", username);
                        using (var reader = cmd.ExecuteReader())
                        {
                            if (reader.Read())
                            {
                                string hash = reader.GetString(0);
                                long playerId = reader.GetInt64(1);
                                
                                if (VerifyHash(password, hash))
                                {
                                    reader.Close();
                                    
                                    // Generate new Link Code
                                    const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                                    var random = new Random();
                                    string newCode = new string(Enumerable.Repeat(chars, 8).Select(s => s[random.Next(s.Length)]).ToArray());
                                    
                                    // Update player's GoogleToken in database so they can use /login in game
                                    using (MySqlCommand updateCmd = new MySqlCommand("UPDATE player SET GoogleToken = @c WHERE AvatarId = @id", conn))
                                    {
                                        updateCmd.Parameters.AddWithValue("@c", newCode);
                                        updateCmd.Parameters.AddWithValue("@id", playerId);
                                        updateCmd.ExecuteNonQuery();
                                    }
                                    
                                    return JsonConvert.SerializeObject(new { success = true, player_id = playerId, code = newCode });
                                }
                            }
                        }
                    }
                }
                return JsonConvert.SerializeObject(new { success = false, error = "Invalid username or password" });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = "Server error: " + ex.Message });
            }
        }

        public static string HandleRegisterApi(string jsonBody)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(jsonBody);
                string username = data.username;
                string password = data.password;
                long playerId = data.player_id;
                string code = data.code;

                string connStr = "Server=" + Configuration.DatabaseHost + ";Port=" + Configuration.DatabasePort + ";Database=" + Configuration.DatabaseName + ";Uid=" + Configuration.DatabaseUser + ";Password=" + Configuration.DatabasePassword + ";";
                using (MySqlConnection conn = new MySqlConnection(connStr))
                {
                    conn.Open();
                    
                    // Verify that the Player ID and Link Code match what's in the player table
                    using (MySqlCommand cmd = new MySqlCommand("SELECT GoogleToken FROM player WHERE AvatarId = @id", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", playerId);
                        object result = cmd.ExecuteScalar();
                        if (result != null && result.ToString().Equals(code, StringComparison.OrdinalIgnoreCase))
                        {
                            // Correct! Now register them in the users table
                            using (MySqlCommand insertCmd = new MySqlCommand("INSERT INTO users (username, password_hash, player_id) VALUES (@u, @p, @id)", conn))
                            {
                                insertCmd.Parameters.AddWithValue("@u", username);
                                insertCmd.Parameters.AddWithValue("@p", CreateHash(password));
                                insertCmd.Parameters.AddWithValue("@id", playerId);
                                
                                try {
                                    insertCmd.ExecuteNonQuery();
                                    return JsonConvert.SerializeObject(new { success = true });
                                } catch (MySqlException e) {
                                    if (e.Number == 1062) return JsonConvert.SerializeObject(new { success = false, error = "Username already exists" });
                                    throw;
                                }
                            }
                        }
                    }
                }
                return JsonConvert.SerializeObject(new { success = false, error = "Invalid Player ID or Link Code" });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = "Server error: " + ex.Message });
            }
        }

        private static string CreateHash(string input)
        {
            using (SHA256 sha256 = SHA256.Create())
            {
                byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(input));
                StringBuilder builder = new StringBuilder();
                for (int i = 0; i < bytes.Length; i++)
                    builder.Append(bytes[i].ToString("x2"));
                return builder.ToString();
            }
        }

        private static bool VerifyHash(string input, string hash)
        {
            return CreateHash(input) == hash;
        }

        public static string GetjsonAPI()
"""

code = code.replace("public static string GetjsonAPI()", api_methods)

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("API.cs patched successfully.")
