using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Threading.Tasks;
using CsvHelper;
using ClearComs.Models;

namespace ClearComs.Services
{
    public static class QuizLoader
    {
        public static async Task<List<QuizQuestion>> LoadFromPackageAsync()
        {
            using var stream = await FileSystem.OpenAppPackageFileAsync("quiz.csv");
            using var reader = new StreamReader(stream);
            using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

            var questions = new List<QuizQuestion>();
            await foreach (var record in csv.GetRecordsAsync<QuizQuestion>())
            {
                questions.Add(record);
            }

            return questions;
        }
    }
}
