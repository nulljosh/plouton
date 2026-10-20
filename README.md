<img src="icon.svg" width="80" style="border-radius:18px">

# Plouton

![version](https://img.shields.io/badge/version-v3.6.2-blue)
![license](https://img.shields.io/badge/license-MIT-green) [![GitHub](https://img.shields.io/badge/GitHub-nulljosh%2Ftalli-black?logo=github)](https://github.com/nulljosh/plouton)

Live at [plouton.jaybulb.com](https://plouton.jaybulb.com) · [App Store](https://apps.apple.com/app/talli/id6782366555)

<p align="center">
  <img src="docs/screenshots/ios-home.png" width="220">
  <img src="docs/screenshots/mac-home.png" width="520">
</p>

When does the money come? How much?

Plouton answers that for people on BC income assistance. It reads BC Self-Serve for you and puts one number on the screen: your next payment.

Free. Always.

## Three tabs

- **Home**: the next payment, big, with the days left. Everything else sits under Details.
- **Status**: PWD, RDSP and CDB, and the benefits you can claim.
- **Messages**: your Self-Serve messages, newest first, on every device.

iPhone, Mac, Apple Watch and web. English, French, Chinese and Punjabi.

## Run

```bash
npm install && npm start
```

Open http://localhost:3000. Copy `.env.example` to `.env`. Runs on Cloudflare Workers; deploy with `npm run deploy`.

## More

[Whitepaper](docs/WHITEPAPER.md) · [API](docs/API.md) · [Architecture](docs/ARCHITECTURE.md) · [Brand kit](brand/index.html) · [Roadmap](roadmap.md) · [Contributing](.github/CONTRIBUTING.md) · [Security](.github/SECURITY.md)

<img src="architecture.svg" width="600">

## License

MIT 2026 Joshua Trommel
