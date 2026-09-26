WEIGHTS = {'architecture':15.0,'security':20.0,'dependencies':15.0,'testing':15.0,'documentation':10.0,'maintainability':15.0,'modernization_readiness':10.0}
if set(WEIGHTS) != {'architecture','security','dependencies','testing','documentation','maintainability','modernization_readiness'} or sum(WEIGHTS.values()) != 100:
    raise RuntimeError('Invalid scoring weights')
