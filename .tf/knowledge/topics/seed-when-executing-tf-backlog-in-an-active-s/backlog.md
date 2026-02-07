# Backlog: seed-when-executing-tf-backlog-in-an-active-s

| ID | Title | Est. Hours | Score | Depends On | Component Tags | Links |
|----|-------|------------|-------|------------|----------------|-------|
| pt-c1yj | Define /tf-backlog session-default topic rules and UX | 1-2 | 6 | - | component:cli, component:docs, component:workflow | pt-m2qh |
| pt-m2qh | Implement /tf-backlog: default topic from active session root_seed | 1-2 | 3 | pt-c1yj | component:api, component:cli, component:config, component:workflow | pt-c1yj, pt-gmpy |
| pt-gmpy | Implement /tf-backlog: include session plan/spike docs as backlog inputs | 1-2 | 3 | pt-m2qh | component:config, component:docs, component:workflow | pt-m2qh, pt-4sw6 |
| pt-4sw6 | Test /tf-backlog session-aware defaulting and inputs | 1-2 | 1 | pt-gmpy | component:docs, component:tests, component:workflow | pt-gmpy |

## Notes
- Dependencies are inferred (seed mode) as a simple chain reflecting intended implementation order.
- Links are added conservatively between adjacent, related tickets.
