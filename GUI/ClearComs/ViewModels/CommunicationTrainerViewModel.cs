using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Threading.Tasks;
using System.Windows.Input;

namespace ClearComs.ViewModels
{
    public partial class CommunicationTrainerViewModel : ObservableObject
    {
        [ObservableProperty]
        private string currentPrompt = "Press 'Play Prompt' to start your communication exercise.";

        [ObservableProperty]
        private string feedbackText = "";

        [ObservableProperty]
        private bool isProcessing = false;

        public ICommand PlayPromptCommand { get; }
        public ICommand RecordCommand { get; }

        public CommunicationTrainerViewModel()
        {
            PlayPromptCommand = new RelayCommand(OnPlayPrompt);
            RecordCommand = new RelayCommand(OnRecord);
        }

        private async void OnPlayPrompt()
        {
            FeedbackText = "Playing prompt...";
            await Task.Delay(1000);
            FeedbackText = "Prompt played. Ready to record!";
        }

        private async void OnRecord()
        {
            IsProcessing = true;
            FeedbackText = "Recording...";
            await Task.Delay(3000);
            IsProcessing = false;
            FeedbackText = "Recording complete! Whisper evaluation coming next.";
        }
    }
}
