# Debi Kurnia

I build AI web tools and the automation that runs behind them.<br>
Founder of [Opustock](https://opustock.com) · Jakarta, Indonesia · Open to freelance and product work

<a href="https://debikurnia.id"><img src="https://img.shields.io/badge/Website-debikurnia.id-6E40C9?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://www.linkedin.com/in/debikurnia"><img src="https://raw.githubusercontent.com/debikurnia/debikurnia/main/assets/badge-linkedin.svg" alt="LinkedIn"></a>
<a href="mailto:kontak@debikurnia.id"><img src="https://img.shields.io/badge/Email-kontak@debikurnia.id-6E40C9?style=for-the-badge&logo=mailbox&logoColor=white" alt="Email"></a>

## Currently building

<a href="https://opustock.com"><img src="https://opustock.com/og.png" alt="Opustock: batch AI tools for stock and video creators" width="640"></a>

**[Opustock](https://opustock.com)** is a suite of batch AI tools for stock and video creators.
**XMeta** generates and cleans Adobe Stock, Vecteezy, Shutterstock, and Dreamstime metadata for a whole batch at once,
flagging risky brand and IP terms before export. **XMotion** turns images into motion prompts for AI video.

Under the hood, users bring their own AI provider key. It lives in an encrypted server-side vault and a proxy injects it
on each request, so it never sits in the browser. With several saved keys, requests fail over between providers automatically.
Release notes are in the [changelog](https://opustock.com/changelog).

On the side: [ElysiumX](https://elysiumx.org), a public experiment in letting AI agents run apps while people keep the final call.

## Open source

### [XSpace](https://github.com/XNyetok/XSpace)

Several isolated browser profiles in one macOS window. Each profile keeps its own cookies, logins, and website data,
so several Google accounts can sit side by side without ever mixing.

- **Light on memory:** native Swift and AppKit on the system WebKit. No Electron, no bundled Chromium. In my test, the same two pages used about 536&nbsp;MB in XSpace versus 964&nbsp;MB in Chrome.
- **Truly separate profiles:** each one is its own persistent WebKit data store, not just a tab group.
- **Private by default:** App Sandbox, Hardened Runtime, no telemetry, no third-party dependencies.

<p>
  <a href="https://github.com/XNyetok/XSpace/releases/latest"><img src="https://img.shields.io/github/v/release/XNyetok/XSpace?style=for-the-badge&label=Download&logo=apple&logoColor=white&color=6E40C9" alt="Download the latest XSpace release"></a>
  <img src="https://img.shields.io/badge/macOS-14%2B-24292F?style=for-the-badge" alt="macOS 14+">
  <img src="https://img.shields.io/github/license/XNyetok/XSpace?style=for-the-badge&color=24292F" alt="License">
</p>

It is still early (the UI is in Indonesian for now and localization is planned), and contributions are welcome.

**Contribution:** traced the Kiro CLI "Always allow" approval loop to its policy compiler turning backslashes into slashes
in shell rules, so a saved rule never matched the command it was saved for. Root cause and a capability-aware fix:
[kirodotdev/Kiro#9507](https://github.com/kirodotdev/Kiro/issues/9507#issuecomment-4808333640).

## Tech I use

<img src="https://skillicons.dev/icons?i=php,laravel,py,js,swift,mysql,tailwind,git&perline=8" alt="PHP, Laravel, Python, JavaScript, Swift, MySQL, Tailwind CSS, Git">

AI integrations:
<img src="https://raw.githubusercontent.com/debikurnia/debikurnia/main/assets/badge-openai.svg" alt="OpenAI">
<img src="https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Anthropic">

## Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/debikurnia/debikurnia/output/snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/debikurnia/debikurnia/output/snake.svg">
  <img alt="My contribution graph, eaten by a snake" src="https://raw.githubusercontent.com/debikurnia/debikurnia/output/snake.svg">
</picture>

## Work with me

I take freelance and product work, mostly:

- AI features for existing web apps: LLM integrations, batch processing, prompt pipelines
- Automation behind the scenes: data cleanup, content workflows, internal tools
- Laravel products, from first version to production
- Small native macOS utilities in Swift

Email [kontak@debikurnia.id](mailto:kontak@debikurnia.id) or start at [debikurnia.id](https://debikurnia.id).

<p>
  <img src="https://img.shields.io/badge/Open_to-Freelance-22C55E?style=for-the-badge&logo=handshake&logoColor=white" alt="Open to freelance">
  <img src="https://hits.sh/github.com/debikurnia.svg?style=for-the-badge&label=Profile%20views&color=6E40C9&labelColor=24292F&extraCount=326" alt="Profile views">
</p>
