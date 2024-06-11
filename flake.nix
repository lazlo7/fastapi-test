{
  description = "Development shell for webserver";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };
  outputs = { self, nixpkgs, poetry2nix, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { 
        system = system;
        config = {
          allowUnfree = true;
        }; 
      };
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      wwwrequef = mkPoetryApplication { 
        projectDir = ./.;
        python = pkgs.python3;
        pyproject = ./pyproject.toml;
        poetryLock = ./poetry.lock; 
      };
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        buildInputs = with pkgs; [
          wwwrequef
        ];    
      };
  };
}
