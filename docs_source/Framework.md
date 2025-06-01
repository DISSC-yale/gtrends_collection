## Components

The Framework aspect of this repository consists of the following components:

1. The `GOOGLE_API_KEY` environment variable, which may be stored in a `.env` file.
2. A pair of `scope` files to define the main collection targets.
3. `scripts` to define different collection tasks.
4. A `data` output directory to write results to.

These make up a structure around which data are collected. By default, they are assumed to be
in the root directory, but each can be redirected with function arguments.

## Automatic Updates

On top of those components, the `.github/workflows/weekply_collection.yaml` file defines
a GitHub action used to perform regular updates.

This depends on the `GOOGLE_API_KEY` being defined in actions secretes (Settings > Secrets and variables > Actions > Secrets)
and actions having write permissions (Settings > Actions > General > Workflow permissions).
