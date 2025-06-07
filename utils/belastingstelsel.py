from typing import Callable

Tarieven = dict[tuple[float, float], Callable[[float], float]]

belastingstelsels: dict[int, dict[str, Tarieven]] = {
    2024: {
        "arbeidskorting": {
            (0, 11491): lambda x: 0.08425 * x,
            (11491, 24821): lambda x: 968 + 0.31433 * (x - 11490),
            (24821, 39958): lambda x: 5158 + 0.02471 * (x - 24820),
            (39958, 124935): lambda x: 5532 - 0.06510 * (x - 39958),
            (124935, float("inf")): lambda x: 0.0,
        },
        "heffingskorting": {
            (0, 24813): lambda x: 3362,
            (24813, 75518): lambda x: 3362 - 0.06630 * (x - 24812),
            (75518, float("inf")): lambda x: 0.0,
        },
        "schijven": {
            (0, 75518): lambda x: 0.3697 * x,
            (75518, float("inf")): lambda x: 0.495 * x,
        },
    },
    2025: {
        "arbeidskorting": {
            (0, 12169): lambda x: 0.08053 * x,
            (12169, 26288): lambda x: 980 + 0.30030 * (x - 12169),
            (26288, 43071): lambda x: 5220 + 0.02258 * (x - 26288),
            (43071, 129078): lambda x: 5599 - 0.06510 * (x - 43071),
            (129078, float("inf")): lambda x: 0.0,
        },
        "heffingskorting": {
            (0, 28406): lambda x: 3068,
            (28406, 76817): lambda x: 3068 - 0.06337 * (x - 28406),
            (76817, float("inf")): lambda x: 0.0,
        },
        "schijven": {
            (0, 38441): lambda x: 0.3582 * x,
            (38441, 76817): lambda x: 0.3748 * x,
            (76817, float("inf")): lambda x: 0.4950 * x,
        },
    },
}
