namespace ClearComs.Pages;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private async void OnFlashcardsClicked(object sender, EventArgs e)
    {
        await Navigation.PushAsync(new FlashcardsPage());
    }

    private async void OnQuizzesClicked(object sender, EventArgs e)
    {
        await Navigation.PushAsync(new QuizPage());
    }

    private async void OnCommunicationClicked(object sender, EventArgs e)
    {
        await Navigation.PushAsync(new CommunicationPage());
    }
}