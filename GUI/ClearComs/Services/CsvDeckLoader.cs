using ClearComs.Models;
using System.Text;

namespace ClearComs.Services
{
    public static class CsvDeckLoader
    {
        // This will be our default file name (inside Resources/Raw/)
        private const string PackageFileName = "flashcards.csv";

        // Loads cards from the packaged CSV file
        public static async Task<List<Flashcard>> LoadFromPackageAsync(string fileName = PackageFileName)
        {
            // Open packaged file (Build Action = MauiAsset)
            using var stream = await FileSystem.OpenAppPackageFileAsync(fileName);
            using var reader = new StreamReader(stream, Encoding.UTF8);

            var cards = new List<Flashcard>();

            // Skip the header line
            _ = await reader.ReadLineAsync();

            string? line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                // Basic CSV splitting — works fine since our data has no commas inside text
                var parts = line.Split(',');
                if (parts.Length >= 2)
                {
                    var front = parts[0].Trim();
                    var back = string.Join(",", parts.Skip(1)).Trim(); // keep commas in back text
                    cards.Add(new Flashcard(front, back));
                }
            }

            return cards;
        }
    }
}
