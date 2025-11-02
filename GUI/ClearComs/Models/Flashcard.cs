namespace ClearComs.Models
{
    public class Flashcard
    {
        // The front text (question, word, or term)
        public string Front { get; set; }

        // The back text (answer or definition)
        public string Back { get; set; }

        // Constructor (sets front and back when creating a card)
        public Flashcard(string front, string back)
        {
            Front = front;
            Back = back;
        }
    }
}
