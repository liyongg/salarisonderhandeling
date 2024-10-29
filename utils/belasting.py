belastingstelsel = {
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
    }
}
