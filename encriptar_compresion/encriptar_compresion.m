function [secret, codigos, ky_pub, ky_pr, n] = encriptar_compresion(mensaje, ruta_entrada, ruta_salida)

    ascii_message = double(mensaje);

    [ascii_message_comprimido, codigos, ~, ~] = compresion_huffman.huffmanComprimir(ascii_message);

    [audio, Fs] = audioread(ruta_entrada);


    % Bug 4 corregido: indexación clara para vector 1D
    num1 = encriptacion_rsa.generador_primos(16);   % 5023
    num2 = encriptacion_rsa.generador_primos(16);  % 5081
    [ky_pub, ky_pr, n] = encriptacion_rsa.def_rsa(num1, num2);
    %fprintf('Llave pública  (e=%d, n=%d)\n', ky_pub, n);
    %fprintf('Llave privada  (d=%d, n=%d)\n', ky_pr, n);
    
    % Cifrado
    secret = zeros(1, length(ascii_message_comprimido));
    for i = 1:length(ascii_message_comprimido)
        secret(i) = encriptacion_rsa.cifrado_rsa(ascii_message_comprimido(i), ky_pub, n);
    end

    if numel(secret) > numel(audio)
        error('El audio no tiene suficientes muestras para ocultar el mensaje comprimido.');
    end
    
    audioEntero = int16(audio * 32767);
    audioUnsigned = uint16(int32(audioEntero) + 32768); % desplazar a rango no-negativo
     
    audioEsteoUnsigned = audioUnsigned;
    for i = 1:numel(secret)
        audioEsteoUnsigned(i) = bitset(audioEsteoUnsigned(i), 1, secret(i));
    end
     
    audioEstego = int16(int32(audioEsteoUnsigned) - 32768); % volver a rango con signo
    audioEstegoFloat = double(audioEstego) / 32767;
     
    % Para guardar el resultado en un .wav:
    audiowrite(ruta_salida, audioEstegoFloat, Fs);

    claves_num = keys(codigos);
    valores = values(codigos);
    
    claves_texto = cell(1, length(claves_num));
    for idx = 1:length(claves_num)
        claves_texto{idx} = num2str(claves_num{idx}); % Convierte 65 en '65'
    end
    
    % Creamos un mapa temporal con llaves de tipo texto (char)
    mapa_temporal = containers.Map(claves_texto, valores);
    
    % Ahora jsonencode funcionará perfectamente sin errores
    codigos = jsonencode(mapa_temporal);
    % disp(codigos);
    
    %fprintf('Original  : %s\n', mensaje);
    %fprintf('Cifrado   : '); disp(secret);
end