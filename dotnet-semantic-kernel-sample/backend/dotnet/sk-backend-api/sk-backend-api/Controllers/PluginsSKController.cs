using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel;
using System.Configuration;

// For more information on enabling Web API for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace sk_backend_api.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PluginsSKController : ControllerBase
    {


        IConfiguration _configuration;
        public PluginsSKController(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        // POST api/<PluginsSKController>
        [HttpPost]
        public async Task<string> PostAsync([FromBody] string value)
        {
            //Create Kernel builder
            var builder = Kernel.CreateBuilder();

            Console.WriteLine(_configuration.GetValue<string>("Azure:OpenAI:EndpointURL"));
            builder.AddAzureOpenAIChatCompletion(deploymentName: _configuration.GetValue<string>("Azure:OpenAI:DeploymentName"),
                                                 endpoint: _configuration.GetValue<string>("Azure:OpenAI:EndpointURL"),
                                                 apiKey: _configuration.GetValue<string>("Azure:OpenAI:Key"));
            var kernel = builder.Build();

            // Load the plugin directory
            var textConvertorPluginsDirectoryPath = Path.Combine(System.IO.Directory.GetCurrentDirectory(), "Plugins", "TextConvertorPlugin");
            // Load the plugin functons
            var textConvertorPluginFunctions = kernel.ImportPluginFromPromptDirectory(textConvertorPluginsDirectoryPath);

            // Set-up the arguments (input)
            var arguments = new KernelArguments();
            arguments.Add("input", value);

            // Invoke the plugin function
            var result = await kernel.InvokeAsync(textConvertorPluginFunctions["GetCustomerData"], arguments);

            //https://github.com/microsoft/semantic-kernel/blob/main/dotnet/README.md
            //https://github.com/microsoft/semantic-kernel/blob/main/dotnet/README.md

            return result.ToString();
        }

    }
}
