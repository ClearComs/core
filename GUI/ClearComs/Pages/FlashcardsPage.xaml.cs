using System;
using ClearComs.ViewModels;
using Microsoft.Maui.Controls;
using Microsoft.Maui;

namespace ClearComs.Views
{
    public partial class FlashcardsPage : ContentPage
    {
        private bool _isAnimating;

        public FlashcardsPage()
        {
            InitializeComponent();
        }

        private async void OnCardTapped(object? sender, EventArgs e)
        {
            if (_isAnimating)
                return;

            if (BindingContext is not FlashcardsViewModel vm)
                return;

            if (FrontView is null || BackView is null)
                return;

            _isAnimating = true;
            try
            {
                // which side is currently visible
                var showingFront = FrontView.IsVisible;
                var visible = showingFront ? FrontView : BackView;
                var hidden = showingFront ? BackView : FrontView;

                // first half: rotate visible to 90�
                await visible.RotateYTo(90, 180, Easing.CubicIn);

                // swap visibility
                visible.IsVisible = false;
                hidden.RotationY = -90; // prepare incoming side
                hidden.IsVisible = true;

                // second half: rotate incoming from -90� to 0�
                await hidden.RotateYTo(0, 180, Easing.CubicOut);

                // update view-model flip state
                vm.FlipCommand?.Execute(null);
            }
            finally
            {
                _isAnimating = false;
            }
        }
    }
}