# FitFlow

![Version](https://img.shields.io/badge/Version-2026.9.2-41BDF5?style=flat-square)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.8%2B-41BDF5?logo=homeassistant)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alves-dev&repository=ha-fit-flow&category=integration)

FitFlow manages flexible gym routines. It recommends the workout that has gone longest without being completed, applies directional recovery conflicts, rotates exercise suggestions, persists active sessions, and records workout/activity history.

[![Quality Gate](https://sonar.alves-dev.com/api/project_badges/measure?project=ha-fit-flow&metric=alert_status)](https://sonar.alves-dev.com/dashboard?id=ha-fit-flow)
[![Coverage](https://sonar.alves-dev.com/api/project_badges/measure?project=ha-fit-flow&metric=coverage)](https://sonar.alves-dev.com/dashboard?id=ha-fit-flow)

## HACS availability

FitFlow is available as a HACS custom repository until it is accepted into the default catalog. Add `https://github.com/alves-dev/ha-fit-flow` as an `Integration` repository in HACS.

## Installation

Install through HACS or copy `custom_components/fit_flow` into your Home Assistant configuration. Restart Home Assistant, then add **FitFlow** through Settings → Devices & services.

## Features

- Configure muscle groups, exercises, workouts, activities, and directional conflict rules in the FitFlow panel.
- Start, resume, finish, or cancel one persisted workout session.
- Use `fit_flow.log_activity` from automations or scripts.
- Monitor the last activity, next workout, and lifetime counters with sensors.

Technical details and contributor checks are in [development documentation](docs/development.md) and [compatibility](docs/compatibility.md).
