using System.Diagnostics;
using System.Text.Json;
using System.IO;

namespace ClearComs.Services
{
    public class PythonBackendService
    {
        private readonly string _pythonPath;
        private readonly string _scriptPath;

        public PythonBackendService()
        {
            // 1) Python çalıştırıcı yolu
            // Eğer cmd'de "python --version" çalışıyorsa bu yeter:
            _pythonPath = "C:\\Users\\yagizcetin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe";

            // 2) Çalışan bin klasöründen proje köküne çık (…\ClearComs\core\GUI\ClearComs\)
            var baseDir = AppContext.BaseDirectory;
            var projectRoot = Path.GetFullPath(
                Path.Combine(baseDir, "..", "..", "..", "..")
            );

            // 3) Python script yolunu buradan kur
            //    Varsayılan: ClearComs\Services\PythonBackend\communications_backend.py
            _scriptPath = Path.Combine(
                projectRoot,
                "Services",
                "PythonBackend",
                "communications_backend.py"
            );

            Debug.WriteLine($"[PY] baseDir     = {baseDir}");
            Debug.WriteLine($"[PY] projectRoot = {projectRoot}");
            Debug.WriteLine($"[PY] scriptPath  = {_scriptPath}");

            if (!File.Exists(_scriptPath))
            {
                Debug.WriteLine("[PY] Script NOT FOUND at: " + _scriptPath);
            }
        }

        /// <summary>
        /// Python scriptine komut gönderir, çıktıyı JSON olarak geri döndürür.
        /// </summary>
        public async Task<Dictionary<string, object>?> RunBackendAsync(string command, int promptId)
        {
            if (!File.Exists(_scriptPath))
            {
                throw new FileNotFoundException(
                    $"Python backend script not found at path: {_scriptPath}"
                );
            }

            var psi = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"\"{_scriptPath}\" {command} {promptId}",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
                // WorkingDirectory vermiyoruz; tam script path'iyle çağırıyoruz
            };

            using var process = new Process { StartInfo = psi };

            process.Start();

            string output = await process.StandardOutput.ReadToEndAsync();
            string error = await process.StandardError.ReadToEndAsync();

            await process.WaitForExitAsync();

            Debug.WriteLine("PYTHON OUT: " + output);
            Debug.WriteLine("PYTHON ERR: " + error);

            if (string.IsNullOrWhiteSpace(output))
                return null;

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                };

                var result = JsonSerializer.Deserialize<Dictionary<string, object>>(output, options);
                return result;
            }
            catch (Exception ex)
            {
                Debug.WriteLine("JSON Parse Error: " + ex.Message);
                return null;
            }
        }
    }
}
