using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows.Input;
using ClearComs.Models;
using ClearComs.Services;

namespace ClearComs.ViewModels
{
    public class FlashcardsViewModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler? PropertyChanged;

        public ObservableCollection<Flashcard> Cards { get; } = new();

        private int _currentIndex;
        private bool _isFlipped;

        public Flashcard? CurrentCard => Cards.Count > 0 ? Cards[_currentIndex] : null;
        public string DisplayText => _isFlipped ? (CurrentCard?.Back ?? "") : (CurrentCard?.Front ?? "");
        public string CounterText => Cards.Count == 0 ? "0/0" : $"{_currentIndex + 1}/{Cards.Count}";

        public ICommand FlipCommand { get; }
        public ICommand NextCommand { get; }
        public ICommand PrevCommand { get; }
        public ICommand ShuffleCommand { get; }

        public FlashcardsViewModel()
        {
            // Create commands (these will be linked to buttons in the XAML)
            FlipCommand = new Command(Flip);
            NextCommand = new Command(Next);
            PrevCommand = new Command(Prev);
            ShuffleCommand = new Command(Shuffle);

            // Start loading the cards
            _ = InitializeAsync();
        }

        private async Task InitializeAsync()
        {
            // Load from your packaged CSV
            var list = await CsvDeckLoader.LoadFromPackageAsync("flashcards.csv");
            foreach (var c in list)
                Cards.Add(c);

            _currentIndex = 0;
            _isFlipped = false;
            NotifyAll();
        }

        private void Flip()
        {
            if (Cards.Count == 0) return;
            _isFlipped = !_isFlipped;
            OnPropertyChanged(nameof(DisplayText));
        }

        private void Next()
        {
            if (Cards.Count == 0) return;
            _currentIndex = (_currentIndex + 1) % Cards.Count;
            _isFlipped = false;
            NotifyAll();
        }

        private void Prev()
        {
            if (Cards.Count == 0) return;
            _currentIndex = (_currentIndex - 1 + Cards.Count) % Cards.Count;
            _isFlipped = false;
            NotifyAll();
        }

        private void Shuffle()
        {
            if (Cards.Count <= 1) return;
            var rnd = new Random();
            var shuffled = Cards.OrderBy(_ => rnd.Next()).ToList();
            Cards.Clear();
            foreach (var c in shuffled) Cards.Add(c);
            _currentIndex = 0;
            _isFlipped = false;
            NotifyAll();
        }

        private void NotifyAll()
        {
            OnPropertyChanged(nameof(CurrentCard));
            OnPropertyChanged(nameof(DisplayText));
            OnPropertyChanged(nameof(CounterText));
        }

        private void OnPropertyChanged(string name)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}
