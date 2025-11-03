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

        // 🎨 Colors and scoring
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
            if (_questions.Count > 0)
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

        private async void OnAnswerSelected(string? choice)
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

            var page = Application.Current?.Windows.FirstOrDefault()?.Page;

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

                // highlight correct one
                if (Current.Answer == Current.OptionA) OptionAColor = "#4CAF50";
                if (Current.Answer == Current.OptionB) OptionBColor = "#4CAF50";
                if (Current.Answer == Current.OptionC) OptionCColor = "#4CAF50";
                if (Current.Answer == Current.OptionD) OptionDColor = "#4CAF50";
            }

            await page?.DisplayAlert(
                isCorrect ? "Correct!" : "Incorrect",
                isCorrect ? $"{selected} is the right answer ✅" : $"Correct answer: {Current.Answer}",
                "OK"
            )!;
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
                _currentIndex = 0;
                Score = 0;
                ScoreDisplay = "Score: 0";
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
    }
}
