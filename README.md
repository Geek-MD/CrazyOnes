# Crazy Ones

_Crazy ones_ is a service designed to automate notifications about software updates for Apple devices.

It relies on two key components to perform its task. The first is a GitHub Actions workflow that scrapes the content of the Apple Updates website in the various languages in which it's available.

The second is a Python script that monitors changes in the HTML files within this repository. Using a Telegram bot, it notifies users about new updates while ignoring those that have already been reported
