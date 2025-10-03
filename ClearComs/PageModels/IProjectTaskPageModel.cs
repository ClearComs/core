using ClearComs.Models;
using CommunityToolkit.Mvvm.Input;

namespace ClearComs.PageModels
{
    public interface IProjectTaskPageModel
    {
        IAsyncRelayCommand<ProjectTask> NavigateToTaskCommand { get; }
        bool IsBusy { get; }
    }
}