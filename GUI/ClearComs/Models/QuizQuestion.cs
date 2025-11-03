namespace ClearComs.Models
{
    public class QuizQuestion
    {
        public string Question { get; set; } = string.Empty;
        public string OptionA { get; set; } = string.Empty;
        public string OptionB { get; set; } = string.Empty;
        public string OptionC { get; set; } = string.Empty;
        public string OptionD { get; set; } = string.Empty;
        public string Answer { get; set; } = string.Empty;

        public bool IsCorrect(string choice)
        {
            return string.Equals(choice, Answer, StringComparison.OrdinalIgnoreCase);
        }
    }
}
