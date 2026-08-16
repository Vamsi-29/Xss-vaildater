# XSS Validator

A Python-based Cross-Site Scripting testing utility that sends payloads to a supplied URL and uses response analysis plus Selenium WebDriver to identify cases where injected JavaScript executes.

## How it works

```text
Target URL
   ↓
Payload injection
   ↓
HTTP response analysis
   ↓
Selenium browser execution check
   ↓
Potential XSS result
```

## Technologies

- Python
- Requests
- Selenium WebDriver
- Browser-based JavaScript execution testing

## Installation

```bash
git clone https://github.com/Vamsi-29/Xss-vaildater.git
cd Xss-vaildater
chmod +x install.sh
./install.sh
```

Run the scanner:

```bash
python3 xss-validater.py
```

## Current limitations

- Designed around URL parameters that accept injected input.
- Targets must use valid URL syntax.
- Browser/Selenium setup is required for execution checks.
- This is a testing aid, not a replacement for manual XSS validation.

## Security note

Use this tool only against applications you own or are explicitly authorized to test. For bug-bounty programs, follow the program's scope and testing rules.

## Project focus

`Web Security` `XSS` `Payload Testing` `Python` `Selenium` `Application Security`
