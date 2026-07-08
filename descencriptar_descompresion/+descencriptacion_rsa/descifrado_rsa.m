function m_rec = descifrado_rsa(c, d, n)
    m_rec = descencriptacion_rsa.modpow(c, d, n);   % ✅ sin desbordamiento
end


