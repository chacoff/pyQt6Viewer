using System;
using System.IO;
using System.Reflection;
using System.Diagnostics;
using System.Threading;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using log4net;
using System.Security.Cryptography;
using System.Configuration;

namespace SeamsShadow
{
    /// <summary>
    /// main program
    /// </summary>
    class Program
    {
        private static readonly ILog log = LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);

        private static IntPtr consoleWindow;
        private static IntPtr hiddenWindow;
        private static NotifyIcon? notifyIcon;
        private static readonly string? MSCpath = ConfigurationManager.AppSettings["msc_path"];
        private static readonly string? EnginePath = ConfigurationManager.AppSettings["engine_path"];
        private static int delay = 5000;

        static async Task Main()
        {
            log.Info("Starting Seams Monitor shadow-mode");

            consoleWindow = Process.GetCurrentProcess().MainWindowHandle;
            hiddenWindow = NativeMethods.CreateHiddenWindow();

            notifyIcon = new NotifyIcon();
            notifyIcon.Icon = new System.Drawing.Icon("ico.ico");
            notifyIcon.Text = "SeamsShadow";
            notifyIcon.Visible = true;

            // handles double click ...
            notifyIcon.DoubleClick += (sender, e) =>
            {
                ShowConsoleWindow();
            };

            MinimizeConsoleWindow();

            await MainThread();

            notifyIcon.Visible = false;
            notifyIcon.Dispose();
            NativeMethods.DestroyWindow(hiddenWindow);
        }

        static async Task MainThread()
        {
            log.Info("Starting main thread");
            while (true)
            {
                await CheckAndStartApplicationsAsync(MSCpath, EnginePath);
            }
        }

        static async Task CheckAndStartApplicationsAsync(string mscPath, string enginePath)
        {
            Task<bool> MscTask = CheckProcessRunningAsync(mscPath);
            Task<bool> EngineTask = CheckProcessRunningAsync(enginePath);

            await Task.WhenAll(MscTask, EngineTask);

            //if (MscTask.Result && EngineTask.Result)
            //{
            //    log.Info("MSC and H-engine are running");
            //}
            
            if (!MscTask.Result)
            {
                StartApplication(mscPath);
                log.Info("MSC re-started");
            }
            
            if (!EngineTask.Result)
            {
                StartApplication(enginePath);
                log.Info("H-engine re-started");
            }
        }

        static async Task<bool> CheckProcessRunningAsync(string processPath)
        {
            await Task.Delay(delay);

            Process[] processes = Process.GetProcessesByName(Path.GetFileNameWithoutExtension(processPath));
            return processes.Length > 0;
        }

        static void StartApplication(string applicationPath)
        {
            Process.Start(applicationPath);
        }

        static void MinimizeConsoleWindow()
        {
            NativeMethods.ShowWindow(consoleWindow, NativeMethods.SW_HIDE);
        }

        static void ShowConsoleWindow()
        {
            NativeMethods.ShowWindow(consoleWindow, NativeMethods.SW_SHOW);
            NativeMethods.SetForegroundWindow(consoleWindow);
        }
    }
}

