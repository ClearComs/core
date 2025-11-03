using ClearComs.Views;
namespace ClearComs.Pages
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();
        }


        private async void OnFlashcardsClicked(object sender, EventArgs e)
        {
            await Shell.Current.GoToAsync("///flashcards");
        }



        private async void OnQuizzesClicked(object sender, EventArgs e)
        {
            await Navigation.PushAsync(new QuizPage());
        }

        private async void OnCommunicationClicked(object sender, EventArgs e)
        {
            await Shell.Current.GoToAsync("///communication");

        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();

            // 👇 This line loads your flashcards from Resources/Raw/flashcards.csv
            var cards = await ClearComs.Services.CsvDeckLoader.LoadFromPackageAsync();

            // 👇 If it loads correctly, you’ll see this in your Debug output window
            Console.WriteLine($"Loaded {cards.Count} flashcards!");
        }
    }
}
