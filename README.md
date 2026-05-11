# Anything GOEWS

Add GOEWS mounting plates to any 3D model. Takes any STL and adds cleats.


## Using in OpenSCAD

Open the `openscad/anything.scad` file and set `model_path` to your original model.
Then set the desired plate and transform parameters to generate the final model.

## Web-based generator

A web-based generator is included that provides a web interface to part generation. The
`openscad` command must be available in the `PATH` for the user running the server and
BOSL2 must be available in the library path.

To run it locally in dev mode:

```bash
make serve
```

The application will be available at http://localhost:5173/

To build for production:

```bash
make server
```

There is Systemd unit definition in `systemd/anything-goews.service`. It assumes the
location of this repo is checked out at `/srv/anything-goews` and a user `goews`
exists. For security reasons, it is highly recommended that nothing under the checkout
is actually writable by the `goews` user.

## License

CC BY-SA 4.0
