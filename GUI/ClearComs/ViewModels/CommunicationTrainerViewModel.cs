using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using ClearComs.Services;
using System.Threading.Tasks;
using System.Windows.Input;


namespace ClearComs.ViewModels
{
    public partial class CommunicationTrainerViewModel : ObservableObject
    {
        private readonly PythonBackendService _backend;

        [ObservableProperty]
        private string currentPrompt = "Press 'Play Prompt' to start your communication exercise.";

        [ObservableProperty]
        private string feedbackText = "";

        [ObservableProperty]
        private bool isProcessing = false;

        private int _currentPromptId = 1; // For Now ID = 1

        public IRelayCommand PlayPromptCommand { get; }
        public IRelayCommand RecordCommand { get; }

        public CommunicationTrainerViewModel()
        {
            _backend = new PythonBackendService();

            PlayPromptCommand = new AsyncRelayCommand(OnPlayPromptAsync);
            RecordCommand = new AsyncRelayCommand(OnRecordAsync);
        }

        private async Task OnPlayPromptAsync()
        {
            IsProcessing = true;
            FeedbackText = "Playing prompt...";

            var result = await _backend.RunBackendAsync("play_prompt", _currentPromptId);

            IsProcessing = false;

            // no answer from backend
            if (result == null)
            {
                FeedbackText = "No response from Python backend.";
                return;
            }

            // 'f python backend g'ves error'
            if (result.TryGetValue("error", out var errObj))
            {
                var msg = errObj?.ToString() ?? "unknown error";
                FeedbackText = $"Python error: {msg}";
                return;
            }

            // succesfull case
            if (result.TryGetValue("prompt_text", out var textObj))
                CurrentPrompt = textObj?.ToString() ?? CurrentPrompt;

            FeedbackText = "Prompt played. Ready to record!";
        }


        private async Task OnRecordAsync()
        {
            // UI: butonları kilitle
            IsProcessing = true;

            // 1) Python komutunu arka planda başlat (hemen await ETME)
            var backendTask = _backend.RunBackendAsync("record_and_evaluate", _currentPromptId);

            // 2) Kullanıcıya aşamaları göster
            FeedbackText = "Preparing microphone...";

            // Tahminen ~2 saniye hazırlık süresi
            await Task.Delay(2000);

            // 3) Kayıt başladı info
            FeedbackText = "Recording (about 5 seconds)... Speak now!";

            // Kullanıcıya 5 saniyelik kayıt süresi hissi ver
            await Task.Delay(5000);

            // 4) Değerlendirme aşaması
            FeedbackText = "Evaluating your speech...";

            // 5) Artık Python'un işini bitirmesini bekliyoruz
            var result = await backendTask;

            IsProcessing = false;

            // Hata / null kontrolleri
            if (result == null)
            {
                FeedbackText = "No response from Python backend.";
                return;
            }

            if (result.TryGetValue("error", out var errObj) && errObj != null)
            {
                var msg = errObj.ToString() ?? "unknown error";
                FeedbackText = $"Python error: {msg}";
                return;
            }

            // Sonuçları al
            string recognized = result.TryGetValue("recognized_text", out var recObj) && recObj != null
                ? recObj.ToString() ?? ""
                : "";

            string score = result.TryGetValue("score", out var scoreObj) && scoreObj != null
                ? scoreObj.ToString() ?? ""
                : "";

            string passed = result.TryGetValue("passed", out var passedObj) && passedObj != null
                ? passedObj.ToString() ?? ""
                : "";

            string feedback = result.TryGetValue("feedback", out var fbObj) && fbObj != null
                ? fbObj.ToString() ?? ""
                : "";

            string verdict = passed == "1" ? "✅ Correct" : "❌ Wrong";

            FeedbackText =
                $"You said:\n{recognized}\n\n" +
                $"{verdict} (Score: {score})\n" +
                (string.IsNullOrWhiteSpace(feedback) ? "" : $"💡 {feedback}");
        }


    }
}
