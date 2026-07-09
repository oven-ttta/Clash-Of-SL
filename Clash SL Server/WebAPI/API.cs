using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using CSS.Core;
using CSS.Helpers;
using MySql.Data.MySqlClient;
using CSS.Logic;
using System.Security.Cryptography;

namespace CSS.WebAPI
{
    internal class API
    {
        private static IPHostEntry ipHostInfo = Dns.Resolve(Dns.GetHostName());
        private static HttpListener Listener;
        private static int Port = Utils.ParseConfigInt("APIPort"); // TODO: Add it to the config File
        private static string IP = ipHostInfo.AddressList[0].ToString();
        private static string URL = "http://" + IP + ":" + Port + "/";

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

        public API()
        {
            new Thread(new ThreadStart(() =>
            {
                try
                {
                    if (!HttpListener.IsSupported)
                    {
                        Logger.Say("The current System doesn't support the WebAPI.");
                        return;
                    }

                    if (Port == 80)
                    {
                        Logger.Say("Can't start the API on Port 80 using now default Port(88)");
                        Port = 88;
                        URL = "http://" + IP + ":" + Port + "/";
                    }

                    Listener = new HttpListener();
                    Listener.Prefixes.Add("http://localhost:" + Port + "/");
                    Listener.Prefixes.Add("http://localhost:" + Port + "/api/");
                    Listener.Prefixes.Add("http://127.0.0.1:" + Port + "/");
                    Listener.Prefixes.Add("http://127.0.0.1:" + Port + "/api/");
                    Listener.Prefixes.Add("http://*:" + Port + "/");
                    Listener.Prefixes.Add("http://*:" + Port + "/api/");
                    Listener.AuthenticationSchemes = AuthenticationSchemes.Anonymous;
                    Listener.Start();

                    Logger.Say("The WebAPI has been started on '" + Port + "'");

                    ThreadPool.QueueUserWorkItem(new WaitCallback((o) =>
                    {
                        while (Listener.IsListening)
                        {
                            ThreadPool.QueueUserWorkItem(new WaitCallback((c) =>
                            {
                                try
                                {
                                    HttpListenerContext ctx = (HttpListenerContext)c;

                                    
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

                                }
                                catch (Exception)
                                {
                                }

                            }), Listener.GetContext());
                        }
                    }));
                }
                catch (Exception)
                {
                    Logger.Say("Please check if the Port '" + Port + "' is not in use.");
                }
            })).Start();
        }

        public static void Stop()
        {
            Listener.Stop();
        }

        public static string GetStatisticHTML()
        {
            try
            {
                return HTML()
                    .Replace("%ONLINEPLAYERS%", ResourcesManager.m_vOnlinePlayers.Count.ToString())
                    .Replace("%INMEMORYPLAYERS%", ResourcesManager.m_vInMemoryLevels.Count.ToString())
                    .Replace("%INMEMORYALLIANCES%", ResourcesManager.GetInMemoryAlliances().Count.ToString())
                    .Replace("%TOTALCONNECTIONS%", ResourcesManager.GetConnectedClients().Count.ToString());
            }
            catch(Exception)
            {
                return "The server encountered an internal error or misconfiguration and was unable to complete your request. (500)";
            }
        }

        
        public static string HandleLoginApi(string jsonBody)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(jsonBody);
                string username = data.username;
                string password = data.password;

                MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder()
                {
                    Server = Utils.ParseConfigString("MysqlIPAddress"),
                    UserID = Utils.ParseConfigString("MysqlUsername"),
                    Port = (uint)Utils.ParseConfigInt("MysqlPort"),
                    Pooling = false,
                    Database = Utils.ParseConfigString("MysqlDatabase"),
                    MinimumPoolSize = 1
                };
                if (!string.IsNullOrWhiteSpace(Utils.ParseConfigString("MysqlPassword")))
                {
                    builder.Password = Utils.ParseConfigString("MysqlPassword");
                }
                string connStr = builder.ToString();
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

                MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder()
                {
                    Server = Utils.ParseConfigString("MysqlIPAddress"),
                    UserID = Utils.ParseConfigString("MysqlUsername"),
                    Port = (uint)Utils.ParseConfigInt("MysqlPort"),
                    Pooling = false,
                    Database = Utils.ParseConfigString("MysqlDatabase"),
                    MinimumPoolSize = 1
                };
                if (!string.IsNullOrWhiteSpace(Utils.ParseConfigString("MysqlPassword")))
                {
                    builder.Password = Utils.ParseConfigString("MysqlPassword");
                }
                string connStr = builder.ToString();
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

        {
            JObject _Data = new JObject
            {
                {"online_players", ResourcesManager.m_vOnlinePlayers.Count.ToString()},
                {"in_mem_players", ResourcesManager.m_vInMemoryLevels.Count.ToString()},
                {"in_mem_alliances", ResourcesManager.GetInMemoryAlliances().Count.ToString()},
                {"connected_sockets", ResourcesManager.GetConnectedClients().Count.ToString()},
                {"all_players", ObjectManager.GetMaxPlayerID()},
                {"all_clans", ObjectManager.GetMaxAllianceID()}
            };
            return JsonConvert.SerializeObject(_Data, Formatting.Indented);
        }
    }
}
