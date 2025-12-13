// Name: check_bottom.mll

{
    MayaPlugin
    {
        Name = "check_bottom";
        Version = 1.0;
        MayaVersion = 2019;
        Commands = [ { Name = "create_pipline_menu"; } ];
        CommandPlugins =
        [
            {
                Name = "create_pipline_menu";
                Language = "Python";
                Script = "path/to/your/script.py";
                CallableFromScriptEditor = true;
            }
        ];
    }
}
