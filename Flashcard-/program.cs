using System;
using System.Collections.Generic;

class Flashcard
{
    public string word;
    public string definition;
    private string top;
    private string bottom;

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
}
public class FlashcardList
{
        public static List<Flashcard> CreateList(List<(string word, string definition)> entries)
    {
        List<Flashcard> flashcards = new List<Flashcard>();

        foreach (var entry in entries)
        {
            flashcards.Add(new Flashcard(entry.word, entry.definition));
        }

        return flashcards;
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
        var inputList = new List<(string word, string definition)>
        {
            ("one", "wow"),
            ("two", "wowow"),
            ("three","wowowow"),
        };
        var flashcards = FlashcardList.CreateList(inputList);

        for (int i = 0; i < flashcards.Count; i++)
        {
            Console.WriteLine($"Card {i}: {flashcards[i].word} - {flashcards[i].definition}");
        }
        
    }
}