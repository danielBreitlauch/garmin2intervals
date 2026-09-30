{ pkgs, lib, config, inputs, ... }:
{
  packages = with pkgs; [
  ];

  dotenv.enable = true;
  languages.python = {
    enable = true;
    version = "3.13";
    venv.enable = true;

    uv = {
      enable = true;
      sync = {
        enable = true;
        allExtras = true;
      };
    };
  };

  enterShell = ''
    export PYTHONPYCACHEPREFIX=$(pwd)/.pyc
  '';
}
