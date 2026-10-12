// =====================================================================
// Auto-Generated Unibots Autonomous Policy Tree (C++ for ESP32 / Arduino)
// Zero external dependencies, executes in ~0.01 ms on microcontrollers
// =====================================================================

#ifndef ESP32_POLICY_TREE_HPP
#define ESP32_POLICY_TREE_HPP

inline void evaluate_policy_tree(const float obs[32], float action[3]) {
    if (obs[31] <= -1.0000f) {
        action[0] = 0.0008f;
        action[1] = 0.0001f;
        action[2] = 0.0001f;
        return;
    } else {
        if (obs[0] <= -0.3037f) {
            if (obs[0] <= -0.5371f) {
                if (obs[0] <= -0.6393f) {
                    if (obs[2] <= -0.2838f) {
                        if (obs[2] <= -0.5336f) {
                            if (obs[13] <= 0.7279f) {
                                if (obs[2] <= -0.7154f) {
                                    if (obs[31] <= -0.9520f) {
                                        action[0] = 1.0000f;
                                        action[1] = -1.0000f;
                                        action[2] = 0.2520f;
                                        return;
                                    } else {
                                        action[0] = 1.0000f;
                                        action[1] = -1.0000f;
                                        action[2] = 0.1065f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.8496f;
                                    action[1] = -0.9944f;
                                    action[2] = -0.0119f;
                                    return;
                                }
                            } else {
                                action[0] = 0.4494f;
                                action[1] = -0.9544f;
                                action[2] = -0.4182f;
                                return;
                            }
                        } else {
                            if (obs[13] <= -0.2721f) {
                                action[0] = -0.6868f;
                                action[1] = -1.0000f;
                                action[2] = -0.3372f;
                                return;
                            } else {
                                action[0] = 0.2488f;
                                action[1] = -0.9170f;
                                action[2] = -0.6847f;
                                return;
                            }
                        }
                    } else {
                        if (obs[31] <= -0.6560f) {
                            if (obs[30] <= 0.0720f) {
                                if (obs[15] <= -0.7455f) {
                                    action[0] = -0.5431f;
                                    action[1] = -0.9762f;
                                    action[2] = 0.0409f;
                                    return;
                                } else {
                                    if (obs[30] <= 0.0598f) {
                                        action[0] = 0.0135f;
                                        action[1] = -0.9194f;
                                        action[2] = -0.7666f;
                                        return;
                                    } else {
                                        action[0] = -0.1572f;
                                        action[1] = -1.0000f;
                                        action[2] = -1.0000f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[31] <= -0.9253f) {
                                    if (obs[23] <= 0.9398f) {
                                        action[0] = 0.0457f;
                                        action[1] = -1.0000f;
                                        action[2] = -0.9916f;
                                        return;
                                    } else {
                                        action[0] = 0.0205f;
                                        action[1] = -1.0000f;
                                        action[2] = -0.6875f;
                                        return;
                                    }
                                } else {
                                    if (obs[23] <= -0.0882f) {
                                        action[0] = 0.6373f;
                                        action[1] = -0.9398f;
                                        action[2] = -0.6410f;
                                        return;
                                    } else {
                                        action[0] = 0.2199f;
                                        action[1] = -0.9551f;
                                        action[2] = -0.8890f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[23] <= -0.0689f) {
                                if (obs[29] <= -0.1320f) {
                                    if (obs[17] <= -0.7464f) {
                                        action[0] = 0.0746f;
                                        action[1] = -0.1144f;
                                        action[2] = 0.8980f;
                                        return;
                                    } else {
                                        action[0] = 0.2834f;
                                        action[1] = -0.3826f;
                                        action[2] = 0.5553f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.1430f;
                                    action[1] = -0.9241f;
                                    action[2] = -0.7611f;
                                    return;
                                }
                            } else {
                                if (obs[31] <= -0.1080f) {
                                    if (obs[30] <= 0.1426f) {
                                        action[0] = 0.0856f;
                                        action[1] = -0.8488f;
                                        action[2] = -0.4080f;
                                        return;
                                    } else {
                                        action[0] = -0.0749f;
                                        action[1] = -1.0000f;
                                        action[2] = -1.0000f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= 0.8547f) {
                                        action[0] = -0.3510f;
                                        action[1] = -0.8277f;
                                        action[2] = 0.1639f;
                                        return;
                                    } else {
                                        action[0] = 0.0642f;
                                        action[1] = -0.9158f;
                                        action[2] = -0.5419f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (obs[2] <= -0.0954f) {
                        if (obs[5] <= -0.3197f) {
                            if (obs[31] <= 0.0827f) {
                                if (obs[5] <= -0.5166f) {
                                    action[0] = 0.1293f;
                                    action[1] = -0.8470f;
                                    action[2] = -0.4127f;
                                    return;
                                } else {
                                    action[0] = 0.5990f;
                                    action[1] = -0.2047f;
                                    action[2] = -0.0629f;
                                    return;
                                }
                            } else {
                                if (obs[5] <= -0.3586f) {
                                    action[0] = -0.0266f;
                                    action[1] = 0.4923f;
                                    action[2] = -0.1613f;
                                    return;
                                } else {
                                    action[0] = 0.7100f;
                                    action[1] = 0.0045f;
                                    action[2] = -0.0179f;
                                    return;
                                }
                            }
                        } else {
                            if (obs[31] <= -0.9200f) {
                                if (obs[2] <= -0.8526f) {
                                    action[0] = 1.0000f;
                                    action[1] = -0.7416f;
                                    action[2] = 0.3894f;
                                    return;
                                } else {
                                    if (obs[31] <= -0.9307f) {
                                        action[0] = 1.0000f;
                                        action[1] = -0.9829f;
                                        action[2] = 0.1316f;
                                        return;
                                    } else {
                                        action[0] = 0.9283f;
                                        action[1] = -0.9222f;
                                        action[2] = -0.0390f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[31] <= -0.1460f) {
                                    if (obs[2] <= -0.4010f) {
                                        action[0] = 0.7199f;
                                        action[1] = -0.6999f;
                                        action[2] = -0.1840f;
                                        return;
                                    } else {
                                        action[0] = 0.5929f;
                                        action[1] = -0.8571f;
                                        action[2] = -0.5505f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= -0.4994f) {
                                        action[0] = 0.8233f;
                                        action[1] = -0.3694f;
                                        action[2] = -0.0681f;
                                        return;
                                    } else {
                                        action[0] = 0.5088f;
                                        action[1] = -0.6951f;
                                        action[2] = -0.2570f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[31] <= -0.5947f) {
                            if (obs[13] <= 0.3175f) {
                                action[0] = 0.6123f;
                                action[1] = -0.5705f;
                                action[2] = -0.1406f;
                                return;
                            } else {
                                if (obs[30] <= 0.0494f) {
                                    action[0] = -0.2638f;
                                    action[1] = -0.3810f;
                                    action[2] = -0.5270f;
                                    return;
                                } else {
                                    if (obs[31] <= -0.9053f) {
                                        action[0] = -0.0952f;
                                        action[1] = -1.0000f;
                                        action[2] = -0.9870f;
                                        return;
                                    } else {
                                        action[0] = 0.2721f;
                                        action[1] = -0.6274f;
                                        action[2] = -0.7522f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[23] <= 0.3346f) {
                                if (obs[17] <= -0.7343f) {
                                    action[0] = 0.0466f;
                                    action[1] = 0.6849f;
                                    action[2] = 1.0000f;
                                    return;
                                } else {
                                    action[0] = 0.3734f;
                                    action[1] = -0.1307f;
                                    action[2] = 0.1805f;
                                    return;
                                }
                            } else {
                                if (obs[2] <= 0.0205f) {
                                    if (obs[0] <= -0.5646f) {
                                        action[0] = 0.5588f;
                                        action[1] = -0.7441f;
                                        action[2] = -0.4712f;
                                        return;
                                    } else {
                                        action[0] = 0.4103f;
                                        action[1] = -0.6300f;
                                        action[2] = -0.0971f;
                                        return;
                                    }
                                } else {
                                    if (obs[29] <= -0.0704f) {
                                        action[0] = 0.2738f;
                                        action[1] = -0.3388f;
                                        action[2] = 0.0767f;
                                        return;
                                    } else {
                                        action[0] = 0.0979f;
                                        action[1] = -0.5387f;
                                        action[2] = -0.3991f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                if (obs[7] <= -0.8152f) {
                    if (obs[0] <= -0.4503f) {
                        if (obs[0] <= -0.4508f) {
                            if (obs[7] <= -0.8153f) {
                                if (obs[21] <= -0.5903f) {
                                    action[0] = 0.0455f;
                                    action[1] = -0.3804f;
                                    action[2] = 0.0026f;
                                    return;
                                } else {
                                    action[0] = 0.4698f;
                                    action[1] = -0.4280f;
                                    action[2] = -0.1048f;
                                    return;
                                }
                            } else {
                                action[0] = 0.0481f;
                                action[1] = -0.3691f;
                                action[2] = 0.0061f;
                                return;
                            }
                        } else {
                            action[0] = 0.0466f;
                            action[1] = -0.3641f;
                            action[2] = 0.0076f;
                            return;
                        }
                    } else {
                        if (obs[0] <= -0.4501f) {
                            action[0] = 0.0472f;
                            action[1] = -0.3554f;
                            action[2] = 0.0103f;
                            return;
                        } else {
                            action[0] = -0.1822f;
                            action[1] = 0.1528f;
                            action[2] = -0.0161f;
                            return;
                        }
                    }
                } else {
                    if (obs[7] <= -0.3773f) {
                        if (obs[13] <= -0.8464f) {
                            if (obs[0] <= -0.4497f) {
                                if (obs[0] <= -0.4499f) {
                                    if (obs[19] <= -0.1768f) {
                                        action[0] = 0.0475f;
                                        action[1] = -0.3594f;
                                        action[2] = 0.0118f;
                                        return;
                                    } else {
                                        action[0] = -0.0194f;
                                        action[1] = 0.1199f;
                                        action[2] = -0.0018f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.0479f;
                                    action[1] = 0.1508f;
                                    action[2] = 0.0136f;
                                    return;
                                }
                            } else {
                                if (obs[0] <= -0.4487f) {
                                    action[0] = 0.0488f;
                                    action[1] = 0.1635f;
                                    action[2] = 0.0178f;
                                    return;
                                } else {
                                    if (obs[7] <= -0.8149f) {
                                        action[0] = 0.0498f;
                                        action[1] = 0.1772f;
                                        action[2] = 0.0223f;
                                        return;
                                    } else {
                                        action[0] = -0.2761f;
                                        action[1] = 0.5220f;
                                        action[2] = 0.0031f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[13] <= -0.1631f) {
                                if (obs[31] <= -0.3367f) {
                                    if (obs[31] <= -0.4853f) {
                                        action[0] = 0.7823f;
                                        action[1] = -0.3905f;
                                        action[2] = -0.2519f;
                                        return;
                                    } else {
                                        action[0] = 0.2875f;
                                        action[1] = 0.5477f;
                                        action[2] = 0.3947f;
                                        return;
                                    }
                                } else {
                                    if (obs[1] <= 0.9746f) {
                                        action[0] = 0.1750f;
                                        action[1] = 0.0426f;
                                        action[2] = -0.0199f;
                                        return;
                                    } else {
                                        action[0] = -0.0332f;
                                        action[1] = 0.5113f;
                                        action[2] = -0.0615f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[7] <= -0.5608f) {
                                    if (obs[31] <= -0.4440f) {
                                        action[0] = -0.5181f;
                                        action[1] = 1.0000f;
                                        action[2] = -0.1380f;
                                        return;
                                    } else {
                                        action[0] = -0.0858f;
                                        action[1] = 0.6786f;
                                        action[2] = 0.0731f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= -0.1908f) {
                                        action[0] = -0.0523f;
                                        action[1] = 0.1958f;
                                        action[2] = -0.5502f;
                                        return;
                                    } else {
                                        action[0] = 0.2849f;
                                        action[1] = 0.5075f;
                                        action[2] = 0.0344f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[15] <= 0.0777f) {
                            if (obs[15] <= -0.7544f) {
                                if (obs[2] <= 0.7808f) {
                                    if (obs[21] <= -0.0270f) {
                                        action[0] = 0.0359f;
                                        action[1] = 0.9304f;
                                        action[2] = 0.9692f;
                                        return;
                                    } else {
                                        action[0] = 0.6294f;
                                        action[1] = 0.7807f;
                                        action[2] = 0.7300f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.5903f;
                                    action[1] = 0.2410f;
                                    action[2] = 0.2919f;
                                    return;
                                }
                            } else {
                                if (obs[23] <= -0.2905f) {
                                    if (obs[23] <= -0.4771f) {
                                        action[0] = 0.6331f;
                                        action[1] = -0.2293f;
                                        action[2] = -0.2093f;
                                        return;
                                    } else {
                                        action[0] = 0.3625f;
                                        action[1] = -0.8937f;
                                        action[2] = -0.7712f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= -0.8720f) {
                                        action[0] = 0.9261f;
                                        action[1] = 0.0088f;
                                        action[2] = 0.1490f;
                                        return;
                                    } else {
                                        action[0] = 0.5548f;
                                        action[1] = -0.0352f;
                                        action[2] = -0.0550f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[1] <= 0.2056f) {
                                if (obs[2] <= 0.5523f) {
                                    if (obs[30] <= 0.2112f) {
                                        action[0] = 0.5899f;
                                        action[1] = -0.1274f;
                                        action[2] = -0.2767f;
                                        return;
                                    } else {
                                        action[0] = 0.4213f;
                                        action[1] = 0.5244f;
                                        action[2] = 0.2801f;
                                        return;
                                    }
                                } else {
                                    if (obs[17] <= 0.4972f) {
                                        action[0] = -0.1589f;
                                        action[1] = 0.6798f;
                                        action[2] = 0.7551f;
                                        return;
                                    } else {
                                        action[0] = 0.1615f;
                                        action[1] = 0.0263f;
                                        action[2] = 0.0351f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[0] <= -0.4809f) {
                                    if (obs[30] <= 0.0052f) {
                                        action[0] = 0.2171f;
                                        action[1] = -0.3898f;
                                        action[2] = -0.0031f;
                                        return;
                                    } else {
                                        action[0] = 0.4759f;
                                        action[1] = -0.7350f;
                                        action[2] = -0.4009f;
                                        return;
                                    }
                                } else {
                                    if (obs[29] <= -0.3461f) {
                                        action[0] = 0.0745f;
                                        action[1] = 0.0065f;
                                        action[2] = -0.0741f;
                                        return;
                                    } else {
                                        action[0] = 0.4276f;
                                        action[1] = -0.2459f;
                                        action[2] = -0.2060f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } else {
            if (obs[1] <= -0.3603f) {
                if (obs[1] <= -0.5928f) {
                    if (obs[2] <= 0.3730f) {
                        if (obs[2] <= -0.1614f) {
                            if (obs[2] <= -0.5734f) {
                                if (obs[31] <= -0.9387f) {
                                    if (obs[15] <= -0.5457f) {
                                        action[0] = 1.0000f;
                                        action[1] = 1.0000f;
                                        action[2] = -0.0836f;
                                        return;
                                    } else {
                                        action[0] = 1.0000f;
                                        action[1] = 0.9983f;
                                        action[2] = -0.2171f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.9600f;
                                    action[1] = 0.9694f;
                                    action[2] = 0.0497f;
                                    return;
                                }
                            } else {
                                if (obs[15] <= 0.7546f) {
                                    if (obs[13] <= 0.7763f) {
                                        action[0] = 0.4920f;
                                        action[1] = 0.6697f;
                                        action[2] = 0.0361f;
                                        return;
                                    } else {
                                        action[0] = 0.1255f;
                                        action[1] = 0.2199f;
                                        action[2] = -0.7779f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= -0.1673f) {
                                        action[0] = 0.3338f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.8244f;
                                        return;
                                    } else {
                                        action[0] = 0.4026f;
                                        action[1] = 0.6594f;
                                        action[2] = 0.0200f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[30] <= -0.1056f) {
                                if (obs[2] <= 0.2477f) {
                                    action[0] = 0.7529f;
                                    action[1] = 0.5970f;
                                    action[2] = -0.0654f;
                                    return;
                                } else {
                                    action[0] = 0.2856f;
                                    action[1] = 0.3854f;
                                    action[2] = 0.1936f;
                                    return;
                                }
                            } else {
                                if (obs[1] <= -0.7104f) {
                                    if (obs[1] <= -0.7793f) {
                                        action[0] = 0.0359f;
                                        action[1] = 0.9516f;
                                        action[2] = 0.9901f;
                                        return;
                                    } else {
                                        action[0] = 0.5302f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.7259f;
                                        return;
                                    }
                                } else {
                                    if (obs[0] <= 0.4847f) {
                                        action[0] = 0.1549f;
                                        action[1] = 0.8712f;
                                        action[2] = 0.1439f;
                                        return;
                                    } else {
                                        action[0] = 0.4502f;
                                        action[1] = 0.8461f;
                                        action[2] = 0.4969f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[0] <= 0.8220f) {
                            if (obs[17] <= -0.6550f) {
                                if (obs[21] <= 0.4268f) {
                                    action[0] = 0.0185f;
                                    action[1] = 1.0000f;
                                    action[2] = 0.9885f;
                                    return;
                                } else {
                                    action[0] = -0.3984f;
                                    action[1] = 1.0000f;
                                    action[2] = 1.0000f;
                                    return;
                                }
                            } else {
                                if (obs[31] <= -0.9387f) {
                                    if (obs[31] <= -0.9520f) {
                                        action[0] = -0.3287f;
                                        action[1] = 0.9964f;
                                        action[2] = 0.9000f;
                                        return;
                                    } else {
                                        action[0] = -0.0512f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.9904f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= -0.0397f) {
                                        action[0] = 0.3251f;
                                        action[1] = 0.9438f;
                                        action[2] = 0.6012f;
                                        return;
                                    } else {
                                        action[0] = 0.0506f;
                                        action[1] = 0.9722f;
                                        action[2] = 0.9088f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[1] <= -0.6744f) {
                                if (obs[29] <= -0.0620f) {
                                    if (obs[13] <= 0.0153f) {
                                        action[0] = 0.6933f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.4521f;
                                        return;
                                    } else {
                                        action[0] = 0.3251f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.9534f;
                                        return;
                                    }
                                } else {
                                    if (obs[15] <= -0.3222f) {
                                        action[0] = 0.2768f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.8622f;
                                        return;
                                    } else {
                                        action[0] = -0.0071f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.9890f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[2] <= 0.5451f) {
                                    if (obs[1] <= -0.6174f) {
                                        action[0] = 0.6166f;
                                        action[1] = 0.9580f;
                                        action[2] = 0.5311f;
                                        return;
                                    } else {
                                        action[0] = 0.6398f;
                                        action[1] = 0.5575f;
                                        action[2] = -0.0012f;
                                        return;
                                    }
                                } else {
                                    if (obs[17] <= 0.6565f) {
                                        action[0] = 0.6640f;
                                        action[1] = 0.9901f;
                                        action[2] = 0.5682f;
                                        return;
                                    } else {
                                        action[0] = 0.3959f;
                                        action[1] = 1.0000f;
                                        action[2] = 0.9547f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (obs[2] <= 0.5858f) {
                        if (obs[31] <= -0.5440f) {
                            if (obs[15] <= -0.2340f) {
                                if (obs[29] <= -0.1837f) {
                                    if (obs[30] <= -0.0922f) {
                                        action[0] = 0.5895f;
                                        action[1] = -0.2197f;
                                        action[2] = -0.3510f;
                                        return;
                                    } else {
                                        action[0] = 0.5580f;
                                        action[1] = 0.8353f;
                                        action[2] = 0.6510f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= -0.9013f) {
                                        action[0] = 0.9555f;
                                        action[1] = 0.4929f;
                                        action[2] = -0.0585f;
                                        return;
                                    } else {
                                        action[0] = 0.5878f;
                                        action[1] = -0.1700f;
                                        action[2] = -0.2741f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[19] <= 0.3662f) {
                                    if (obs[29] <= -0.1883f) {
                                        action[0] = 0.6867f;
                                        action[1] = -0.6590f;
                                        action[2] = -0.7681f;
                                        return;
                                    } else {
                                        action[0] = 0.5220f;
                                        action[1] = 0.5029f;
                                        action[2] = 0.2968f;
                                        return;
                                    }
                                } else {
                                    if (obs[13] <= 0.7293f) {
                                        action[0] = 0.8951f;
                                        action[1] = 0.7957f;
                                        action[2] = 0.2086f;
                                        return;
                                    } else {
                                        action[0] = 0.4360f;
                                        action[1] = 0.7971f;
                                        action[2] = 0.6971f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[1] <= -0.4581f) {
                                if (obs[29] <= -0.2800f) {
                                    if (obs[29] <= -0.4662f) {
                                        action[0] = 0.4505f;
                                        action[1] = 0.8265f;
                                        action[2] = 0.5684f;
                                        return;
                                    } else {
                                        action[0] = 0.2983f;
                                        action[1] = 0.4315f;
                                        action[2] = -0.0251f;
                                        return;
                                    }
                                } else {
                                    if (obs[29] <= 0.0956f) {
                                        action[0] = 0.4046f;
                                        action[1] = 0.1367f;
                                        action[2] = -0.2210f;
                                        return;
                                    } else {
                                        action[0] = 0.4496f;
                                        action[1] = 0.4408f;
                                        action[2] = -0.0288f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[13] <= -0.2616f) {
                                    if (obs[5] <= -0.5194f) {
                                        action[0] = -0.2949f;
                                        action[1] = 0.5810f;
                                        action[2] = 0.0297f;
                                        return;
                                    } else {
                                        action[0] = 0.2666f;
                                        action[1] = 0.0292f;
                                        action[2] = -0.0693f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= -0.1096f) {
                                        action[0] = 0.6183f;
                                        action[1] = -0.1501f;
                                        action[2] = -0.1963f;
                                        return;
                                    } else {
                                        action[0] = 0.4179f;
                                        action[1] = 0.1144f;
                                        action[2] = -0.0452f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[19] <= -0.2690f) {
                            if (obs[0] <= 0.4448f) {
                                if (obs[17] <= -0.1979f) {
                                    if (obs[29] <= 0.0522f) {
                                        action[0] = 0.0855f;
                                        action[1] = 0.8452f;
                                        action[2] = 0.8749f;
                                        return;
                                    } else {
                                        action[0] = 0.4163f;
                                        action[1] = 0.3005f;
                                        action[2] = 0.1982f;
                                        return;
                                    }
                                } else {
                                    action[0] = 0.4754f;
                                    action[1] = -0.0069f;
                                    action[2] = -0.0152f;
                                    return;
                                }
                            } else {
                                if (obs[31] <= -0.8080f) {
                                    action[0] = 0.5750f;
                                    action[1] = -0.8735f;
                                    action[2] = -0.8332f;
                                    return;
                                } else {
                                    if (obs[19] <= -0.5914f) {
                                        action[0] = 0.4094f;
                                        action[1] = -0.5607f;
                                        action[2] = -0.5495f;
                                        return;
                                    } else {
                                        action[0] = 0.4081f;
                                        action[1] = 0.1149f;
                                        action[2] = 0.0495f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[29] <= -0.0603f) {
                                if (obs[31] <= -0.2747f) {
                                    if (obs[17] <= -0.3458f) {
                                        action[0] = -0.0644f;
                                        action[1] = 0.6352f;
                                        action[2] = 0.6612f;
                                        return;
                                    } else {
                                        action[0] = 0.3440f;
                                        action[1] = 0.2082f;
                                        action[2] = -0.1053f;
                                        return;
                                    }
                                } else {
                                    if (obs[0] <= 0.2913f) {
                                        action[0] = 0.1553f;
                                        action[1] = 0.3620f;
                                        action[2] = 0.2543f;
                                        return;
                                    } else {
                                        action[0] = 0.2119f;
                                        action[1] = 0.7683f;
                                        action[2] = 0.7044f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[31] <= 0.2933f) {
                                    if (obs[21] <= -0.5088f) {
                                        action[0] = 0.1756f;
                                        action[1] = 0.4592f;
                                        action[2] = 0.3074f;
                                        return;
                                    } else {
                                        action[0] = 0.2085f;
                                        action[1] = 0.9282f;
                                        action[2] = 0.9199f;
                                        return;
                                    }
                                } else {
                                    if (obs[0] <= 0.2404f) {
                                        action[0] = 0.3987f;
                                        action[1] = 0.2844f;
                                        action[2] = 0.0361f;
                                        return;
                                    } else {
                                        action[0] = 0.2588f;
                                        action[1] = 0.8523f;
                                        action[2] = 0.4146f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                if (obs[29] <= -0.3003f) {
                    if (obs[7] <= 0.4898f) {
                        if (obs[7] <= -0.2999f) {
                            if (obs[29] <= -0.5848f) {
                                if (obs[29] <= -0.6799f) {
                                    action[0] = 0.5756f;
                                    action[1] = 0.0130f;
                                    action[2] = -0.1225f;
                                    return;
                                } else {
                                    if (obs[31] <= -0.3267f) {
                                        action[0] = 0.1959f;
                                        action[1] = 0.8555f;
                                        action[2] = 0.0963f;
                                        return;
                                    } else {
                                        action[0] = 0.1703f;
                                        action[1] = 0.3137f;
                                        action[2] = -0.0954f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[19] <= 0.3277f) {
                                    if (obs[21] <= -0.4668f) {
                                        action[0] = -0.2160f;
                                        action[1] = -0.4044f;
                                        action[2] = -0.1044f;
                                        return;
                                    } else {
                                        action[0] = 0.1232f;
                                        action[1] = 0.4985f;
                                        action[2] = 0.2675f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= -0.3680f) {
                                        action[0] = -0.0398f;
                                        action[1] = 0.8407f;
                                        action[2] = 0.2320f;
                                        return;
                                    } else {
                                        action[0] = -0.3875f;
                                        action[1] = 0.5614f;
                                        action[2] = -0.0399f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[15] <= -0.6315f) {
                                if (obs[23] <= -0.4967f) {
                                    action[0] = 0.1722f;
                                    action[1] = 0.4253f;
                                    action[2] = 0.5708f;
                                    return;
                                } else {
                                    action[0] = 0.2733f;
                                    action[1] = 0.8865f;
                                    action[2] = 0.7260f;
                                    return;
                                }
                            } else {
                                if (obs[19] <= -0.2989f) {
                                    action[0] = 0.1405f;
                                    action[1] = -0.1809f;
                                    action[2] = -0.2415f;
                                    return;
                                } else {
                                    if (obs[7] <= -0.2623f) {
                                        action[0] = 0.5509f;
                                        action[1] = 0.3975f;
                                        action[2] = 0.2320f;
                                        return;
                                    } else {
                                        action[0] = 0.6308f;
                                        action[1] = -0.0989f;
                                        action[2] = -0.0971f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[30] <= 0.1971f) {
                            if (obs[15] <= -0.2144f) {
                                if (obs[31] <= -0.1327f) {
                                    if (obs[21] <= -0.3573f) {
                                        action[0] = 0.0334f;
                                        action[1] = 0.0049f;
                                        action[2] = -0.0273f;
                                        return;
                                    } else {
                                        action[0] = 0.2136f;
                                        action[1] = 0.6482f;
                                        action[2] = 0.5955f;
                                        return;
                                    }
                                } else {
                                    if (obs[23] <= 0.5261f) {
                                        action[0] = 0.5858f;
                                        action[1] = -0.5248f;
                                        action[2] = -0.4779f;
                                        return;
                                    } else {
                                        action[0] = 0.2571f;
                                        action[1] = 0.3365f;
                                        action[2] = 0.3231f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[29] <= -0.3672f) {
                                    if (obs[5] <= -0.1524f) {
                                        action[0] = 0.1863f;
                                        action[1] = 0.6080f;
                                        action[2] = -0.1389f;
                                        return;
                                    } else {
                                        action[0] = 0.4631f;
                                        action[1] = 0.0800f;
                                        action[2] = 0.0734f;
                                        return;
                                    }
                                } else {
                                    if (obs[0] <= -0.0218f) {
                                        action[0] = 0.4986f;
                                        action[1] = -0.4540f;
                                        action[2] = -0.4623f;
                                        return;
                                    } else {
                                        action[0] = 0.5099f;
                                        action[1] = -0.1863f;
                                        action[2] = -0.1511f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[30] <= 0.4417f) {
                                if (obs[29] <= -0.5684f) {
                                    if (obs[31] <= 0.2887f) {
                                        action[0] = 0.5444f;
                                        action[1] = 0.1708f;
                                        action[2] = 0.0830f;
                                        return;
                                    } else {
                                        action[0] = 0.1597f;
                                        action[1] = 0.7570f;
                                        action[2] = 0.7910f;
                                        return;
                                    }
                                } else {
                                    if (obs[0] <= 0.2761f) {
                                        action[0] = 0.3521f;
                                        action[1] = 0.3373f;
                                        action[2] = 0.3394f;
                                        return;
                                    } else {
                                        action[0] = 0.4878f;
                                        action[1] = 0.1107f;
                                        action[2] = -0.0340f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[0] <= 0.8871f) {
                                    if (obs[1] <= -0.0814f) {
                                        action[0] = 0.0160f;
                                        action[1] = 0.9033f;
                                        action[2] = 0.9292f;
                                        return;
                                    } else {
                                        action[0] = 0.5204f;
                                        action[1] = 0.4706f;
                                        action[2] = 0.6463f;
                                        return;
                                    }
                                } else {
                                    if (obs[29] <= -0.4202f) {
                                        action[0] = 0.2850f;
                                        action[1] = 0.7728f;
                                        action[2] = 0.8193f;
                                        return;
                                    } else {
                                        action[0] = 0.4563f;
                                        action[1] = 0.3021f;
                                        action[2] = 0.2715f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (obs[2] <= 0.1248f) {
                        if (obs[13] <= 0.1474f) {
                            if (obs[31] <= -0.8667f) {
                                if (obs[1] <= 0.2489f) {
                                    if (obs[2] <= -0.8774f) {
                                        action[0] = 1.0000f;
                                        action[1] = -0.4836f;
                                        action[2] = -0.4874f;
                                        return;
                                    } else {
                                        action[0] = 0.9171f;
                                        action[1] = -0.0654f;
                                        action[2] = -0.0237f;
                                        return;
                                    }
                                } else {
                                    if (obs[2] <= -0.8015f) {
                                        action[0] = 1.0000f;
                                        action[1] = 0.3639f;
                                        action[2] = 0.3077f;
                                        return;
                                    } else {
                                        action[0] = 0.8806f;
                                        action[1] = 0.0448f;
                                        action[2] = 0.0321f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[17] <= -0.5122f) {
                                    if (obs[2] <= -0.2304f) {
                                        action[0] = 0.5956f;
                                        action[1] = 0.1957f;
                                        action[2] = 0.1795f;
                                        return;
                                    } else {
                                        action[0] = 0.2573f;
                                        action[1] = 0.5616f;
                                        action[2] = 0.3311f;
                                        return;
                                    }
                                } else {
                                    if (obs[5] <= -0.2365f) {
                                        action[0] = 0.0556f;
                                        action[1] = 0.2332f;
                                        action[2] = -0.2545f;
                                        return;
                                    } else {
                                        action[0] = 0.5128f;
                                        action[1] = 0.0148f;
                                        action[2] = -0.0631f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[31] <= 0.1680f) {
                                if (obs[29] <= -0.2052f) {
                                    if (obs[30] <= 0.0077f) {
                                        action[0] = 0.2698f;
                                        action[1] = 0.3634f;
                                        action[2] = 0.2666f;
                                        return;
                                    } else {
                                        action[0] = 0.3990f;
                                        action[1] = -0.1246f;
                                        action[2] = -0.2997f;
                                        return;
                                    }
                                } else {
                                    if (obs[2] <= -0.1673f) {
                                        action[0] = 0.5119f;
                                        action[1] = -0.1959f;
                                        action[2] = -0.2412f;
                                        return;
                                    } else {
                                        action[0] = 0.6304f;
                                        action[1] = 0.0322f;
                                        action[2] = 0.1133f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[0] <= 0.8439f) {
                                    if (obs[30] <= 0.1418f) {
                                        action[0] = 0.3450f;
                                        action[1] = -0.3441f;
                                        action[2] = -0.3374f;
                                        return;
                                    } else {
                                        action[0] = 0.1806f;
                                        action[1] = -0.5429f;
                                        action[2] = -0.6533f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= -0.0655f) {
                                        action[0] = 0.5100f;
                                        action[1] = -0.6334f;
                                        action[2] = -0.5939f;
                                        return;
                                    } else {
                                        action[0] = 0.3877f;
                                        action[1] = -0.0200f;
                                        action[2] = -0.0719f;
                                        return;
                                    }
                                }
                            }
                        }
                    } else {
                        if (obs[1] <= 0.2299f) {
                            if (obs[29] <= 0.1269f) {
                                if (obs[29] <= 0.0549f) {
                                    if (obs[2] <= 0.4275f) {
                                        action[0] = 0.3874f;
                                        action[1] = 0.3318f;
                                        action[2] = 0.1486f;
                                        return;
                                    } else {
                                        action[0] = 0.1176f;
                                        action[1] = 0.4113f;
                                        action[2] = 0.4133f;
                                        return;
                                    }
                                } else {
                                    if (obs[30] <= 0.2046f) {
                                        action[0] = 0.3743f;
                                        action[1] = -0.1238f;
                                        action[2] = -0.1808f;
                                        return;
                                    } else {
                                        action[0] = 0.1703f;
                                        action[1] = 0.7544f;
                                        action[2] = 0.4307f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[30] <= -0.0415f) {
                                    if (obs[30] <= -0.1091f) {
                                        action[0] = 0.5874f;
                                        action[1] = -0.5017f;
                                        action[2] = -0.6281f;
                                        return;
                                    } else {
                                        action[0] = 0.7653f;
                                        action[1] = 0.0211f;
                                        action[2] = -0.3093f;
                                        return;
                                    }
                                } else {
                                    if (obs[2] <= 0.5413f) {
                                        action[0] = 0.4995f;
                                        action[1] = 0.2401f;
                                        action[2] = -0.1453f;
                                        return;
                                    } else {
                                        action[0] = 0.4867f;
                                        action[1] = 0.6477f;
                                        action[2] = 0.1938f;
                                        return;
                                    }
                                }
                            }
                        } else {
                            if (obs[29] <= 0.0517f) {
                                if (obs[21] <= 0.1204f) {
                                    if (obs[31] <= -0.2160f) {
                                        action[0] = 0.1288f;
                                        action[1] = 0.1141f;
                                        action[2] = 0.0974f;
                                        return;
                                    } else {
                                        action[0] = 0.1449f;
                                        action[1] = 0.5874f;
                                        action[2] = 0.6946f;
                                        return;
                                    }
                                } else {
                                    if (obs[31] <= -0.1227f) {
                                        action[0] = 0.5403f;
                                        action[1] = -0.1298f;
                                        action[2] = -0.1673f;
                                        return;
                                    } else {
                                        action[0] = 0.2351f;
                                        action[1] = 0.3816f;
                                        action[2] = 0.0306f;
                                        return;
                                    }
                                }
                            } else {
                                if (obs[31] <= -0.5180f) {
                                    if (obs[1] <= 0.2576f) {
                                        action[0] = 0.1030f;
                                        action[1] = -0.4984f;
                                        action[2] = -0.6346f;
                                        return;
                                    } else {
                                        action[0] = 0.3600f;
                                        action[1] = -0.0827f;
                                        action[2] = 0.0745f;
                                        return;
                                    }
                                } else {
                                    if (obs[13] <= -0.1689f) {
                                        action[0] = 0.3688f;
                                        action[1] = 0.0479f;
                                        action[2] = -0.1256f;
                                        return;
                                    } else {
                                        action[0] = 0.7082f;
                                        action[1] = -0.1826f;
                                        action[2] = 0.0233f;
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

#endif // ESP32_POLICY_TREE_HPP
