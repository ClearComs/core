using System;
using System.Collections.Generic;

public class Flashcard
{
    public string word;
    public string definition;
    public string top;
    public string bottom;

    public Flashcard(string wordCard, string definitionCard)
    {
        word = wordCard;
        definition = definitionCard;
        top = word;
        bottom = definition;
    }

    public string return_top()
    {
        return top;
    }
    public string flip_top()
    {
        string temp = top;
        top = bottom;
        bottom = temp;
        return top;
    }

        public string reset_top()
    {
        top = word;
        bottom = definition;
        return top;
    }
}
public class FlashcardList
{
    public static List<Flashcard> CreateList(List<(string word, string definition)> entries)
    {
        List<Flashcard> flashcards = new List<Flashcard>();

        foreach (var entry in entries)
        {
            flashcards.Add(new Flashcard(entry.Item1, entry.Item2));
        }

        return flashcards;
    }
}

public class FlashcardNavigator
{
    private List<Flashcard> flashcards;
    private int currentIndex;

    public FlashcardNavigator(List<Flashcard> flashcards)
    {
        this.flashcards = flashcards;
        currentIndex = 0;
    }

    public Flashcard GetFirst()
    {
        currentIndex = 0;
        return flashcards.Count > 0 ? flashcards[0] : null;
    }

    public Flashcard GetNext()
    {
        if (currentIndex < flashcards.Count - 1)
        {
            currentIndex++;
            return flashcards[currentIndex];
        }
        return null; // Already at the end
    }

    public Flashcard GetPrevious()
    {
        if (currentIndex > 0)
        {
            currentIndex--;
            return flashcards[currentIndex];
        }
        return null; // Already at the beginning
    }

    public Flashcard GetCurrent()
    {
        return flashcards.Count > 0 ? flashcards[currentIndex] : null;
    }
}


class Program
{
    static void Main(string[] args)
    {
        Flashcard One = new Flashcard("One", "denotes a single, as opposed to none or multiple");
        Console.WriteLine(One.word);
        Console.WriteLine(One.definition);
        Console.WriteLine(One.return_top());
        Console.WriteLine(One.flip_top());
        var inputList = new List<(string, string)>
        {
            ("one", "wow"),
            ("two", "wowow"),
            ("three","wowowow"),
        };
        var flashcards_nr = FlashcardList.CreateList(inputList);

        var navigator = new FlashcardNavigator(flashcards_nr);
        Console.WriteLine(navigator.GetFirst().top);     // One
		Console.WriteLine(navigator.GetFirst().flip_top());     // wow
        Console.WriteLine(navigator.GetNext().top);      // Two
        Console.WriteLine(navigator.GetNext().top);      // Three
        Console.WriteLine(navigator.GetPrevious().top);  // Two
        Console.WriteLine(navigator.GetCurrent().top);   // Two
    }

}

