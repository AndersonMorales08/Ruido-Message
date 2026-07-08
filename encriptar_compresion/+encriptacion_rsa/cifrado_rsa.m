function c = cifrado_rsa(m, e, n)
    c = encriptacion_rsa.modpow(m, e, n);   % ✅ sin desbordamiento
end