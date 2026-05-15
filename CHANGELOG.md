# Changelog

## [1.0.1] - 2026-05-14

### Changed

- Improve the README structure with a clearer quick start, configuration reference, Docker Compose
  guidance, and systemd backup directory details
  ([`5d2d19e`](https://github.com/octivi/unfbackup/commit/5d2d19ef0e2b340ba4b5b23635382c5630fe5865))
  (Marcin Engelmann)
- Align the systemd installation steps in the README and generated release notes
  ([`e677fac`](https://github.com/octivi/unfbackup/commit/e677fac4ea8509d4c85963c0e96bd5344519536d))
  (Marcin Engelmann)

## [1.0.0] - 2026-05-13

### Added

- Add a UniFi OS backup downloader that logs in to a controller, downloads the backup file, logs
  out, and stores the result in a configured destination directory
  ([`1a488b7`](https://github.com/octivi/unfbackup/commit/1a488b77f0cd2e40639d31e76f24ddec85b5dead))
  (Marcin Engelmann)
- Add environment-based configuration for controller credentials, destination directory, fixed
  destination filenames, and optional insecure TLS handling
  ([`1a488b7`](https://github.com/octivi/unfbackup/commit/1a488b77f0cd2e40639d31e76f24ddec85b5dead))
  (Marcin Engelmann)
- Add documented local Python, Docker, Docker Compose, scheduler, and systemd usage paths
  ([`1a488b7`](https://github.com/octivi/unfbackup/commit/1a488b77f0cd2e40639d31e76f24ddec85b5dead))
  (Marcin Engelmann)

[1.0.1]: https://github.com/octivi/unfbackup/releases/tag/v1.0.1
[1.0.0]: https://github.com/octivi/unfbackup/releases/tag/v1.0.0
