using ClearComs.Models;
using ClearComs.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Maui.Controls;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Input;

namespace ClearComs.ViewModels
{
    public partial class QuizViewModel : ObservableObject
    {
        private List<QuizQuestion> _questions = new();
        private int _currentIndex = 0;
        private bool _answered = false;

        [ObservableProperty] private string? currentQuestionText;
        [ObservableProperty] private string? optionA;
        [ObservableProperty] private string? optionB;
        [ObservableProperty] private string? optionC;
        [ObservableProperty] private string? optionD;
        [ObservableProperty] private string? questionCounter;
        [ObservableProperty] private string nextButtonText = "Next";
        [ObservableProperty] private bool isNextVisible = false;

        // Colors and scoring
        [ObservableProperty] private string optionAColor = "#2196F3";
        [ObservableProperty] private string optionBColor = "#2196F3";
        [ObservableProperty] private string optionCColor = "#2196F3";
        [ObservableProperty] private string optionDColor = "#2196F3";
        [ObservableProperty] private int score = 0;

        [ObservableProperty] private string scoreDisplay = "Score: 0";


        private QuizQuestion Current => _questions[_currentIndex];

        public ICommand AnswerCommand { get; }
        public ICommand NextCommand { get; }

        public QuizViewModel()
        {
            AnswerCommand = new RelayCommand<string?>(OnAnswerSelected);
            NextCommand = new RelayCommand(OnNext);
            _ = LoadQuestions();
        }

        private async Task LoadQuestions()
        {
            _questions = await QuizLoader.LoadFromPackageAsync();

            if (_questions is null || _questions.Count == 0)
                return;

            // Shuffle questions and shuffle answers for each question
            ShuffleQuestionsAndAnswers();

            _currentIndex = 0;
            DisplayCurrentQuestion();
        }

        private void DisplayCurrentQuestion()
        {
            var q = Current;
            CurrentQuestionText = q.Question;
            OptionA = q.OptionA;
            OptionB = q.OptionB;
            OptionC = q.OptionC;
            OptionD = q.OptionD;
            QuestionCounter = $"{_currentIndex + 1} / {_questions.Count}";
            IsNextVisible = false;
            _answered = false;

            // reset button colors
            OptionAColor = OptionBColor = OptionCColor = OptionDColor = "#2196F3";
        }

        private void OnAnswerSelected(string? choice)
        {
            if (_answered || choice is null)
                return;

            _answered = true;
            IsNextVisible = true;

            string? selected = choice switch
            {
                "A" => Current.OptionA,
                "B" => Current.OptionB,
                "C" => Current.OptionC,
                "D" => Current.OptionD,
                _ => null
            };

            if (selected is null)
                return;

            bool isCorrect = Current.IsCorrect(selected);

            if (isCorrect)
            {
                Score++;
                ScoreDisplay = $"Score: {Score}";
                SetOptionColor(choice, "#4CAF50"); // green
            }
            else
            {
                SetOptionColor(choice, "#F44336"); // red

                // highlight correct one (Answer is the correct answer text; options were shuffled)
                if (string.Equals(Current.Answer, Current.OptionA, StringComparison.Ordinal)) OptionAColor = "#4CAF50";
                if (string.Equals(Current.Answer, Current.OptionB, StringComparison.Ordinal)) OptionBColor = "#4CAF50";
                if (string.Equals(Current.Answer, Current.OptionC, StringComparison.Ordinal)) OptionCColor = "#4CAF50";
                if (string.Equals(Current.Answer, Current.OptionD, StringComparison.Ordinal)) OptionDColor = "#4CAF50";
            }

            // Note: removed the DisplayAlert popup here to keep feedback inline (colors/score).
        }


        private async void OnNext()
        {
            _currentIndex++;
            var page = Application.Current?.Windows.FirstOrDefault()?.Page;

            if (_currentIndex >= _questions.Count)
            {
                await page?.DisplayAlert(
                    "Quiz Complete 🎉",
                    $"You’ve reached the end of the quiz.\n\nFinal Score: {Score} / {_questions.Count}",
                    "OK"
                )!;

                // reset and reshuffle for a new run
                _currentIndex = 0;
                Score = 0;
                ScoreDisplay = "Score: 0";

                if (_questions.Count > 0)
                {
                    ShuffleQuestionsAndAnswers();
                }
            }

            DisplayCurrentQuestion();
        }

        private void SetOptionColor(string option, string color)
        {
            switch (option)
            {
                case "A": OptionAColor = color; break;
                case "B": OptionBColor = color; break;
                case "C": OptionCColor = color; break;
                case "D": OptionDColor = color; break;
            }
        }

        // ----- Utility: shuffling -----
        private void ShuffleQuestionsAndAnswers()
        {
            // shuffle question order
            Shuffle(_questions);

            // for each question shuffle its options but keep Answer as the correct answer text
            foreach (var q in _questions)
            {
                var options = new List<string> { q.OptionA, q.OptionB, q.OptionC, q.OptionD };
                Shuffle(options);

                q.OptionA = options[0];
                q.OptionB = options[1];
                q.OptionC = options[2];
                q.OptionD = options[3];
                // q.Answer remains unchanged (it contains the correct answer text)
            }
        }

        private static void Shuffle<T>(IList<T> list)
        {
            if (list is null || list.Count <= 1)
                return;

            var rng = Random.Shared;
            for (int i = list.Count - 1; i > 0; i--)
            {
                int j = rng.Next(i + 1);
                (list[i], list[j]) = (list[j], list[i]);
            }
        }
    }
}
