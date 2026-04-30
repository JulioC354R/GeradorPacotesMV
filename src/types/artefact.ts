export interface Artefact {
  name: string
  type: string
  path: string
  module: string
  version: string
  repo_path: string
  build_path: string
}

export interface RepoInfo {
  module: string
  version: string
}
