{
  inputs = {
    nixpkgs = {};
    systems.flake = false;
  };

  outputs = inputs: let
    inherit (inputs.nixpkgs) lib;
    defaultSystems = import inputs.systems;
    argsForSystem = system: {
      pkgs = inputs.nixpkgs.legacyPackages.${system};
    };
    allArgs = lib.genAttrs defaultSystems argsForSystem;
    eachSystem = fn: lib.genAttrs defaultSystems (system: fn allArgs."${system}");
  in {
    formatter = eachSystem ({pkgs, ...}:
      pkgs.writeShellScriptBin "formatter" ''
        ${pkgs.alejandra}/bin/alejandra flake.nix
      '');

    devShells = eachSystem ({pkgs, ...}: {
      default = pkgs.mkShell {
        name = "auto_mirror";
        nativeBuildInputs = [
          (pkgs.python3.withPackages (p: [
            p.python-lsp-server

            p.pygithub
          ]))
        ];
      };
    });
  };
}
