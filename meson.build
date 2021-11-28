project(
  'booth',
  'rust',
  version: '0.1.0',
  license: 'GPL-3.0-or-later',
  meson_version: '>= 0.50.0',
)

cargo_sources = files(
  'Cargo.toml',
  'Cargo.lock',
)

dependency('glib-2.0', version: '>= 2.66')
dependency('gio-2.0', version: '>= 2.66')

subdir('src')
