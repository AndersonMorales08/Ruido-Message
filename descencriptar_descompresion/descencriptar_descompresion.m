function messagge_recovered = descencriptar_descompresion(secret, ky_pr, n, codigos, len_message, ruta_entrada)
    [audio, Fs] = audioread(ruta_entrada);
    
    audioEntero = int16(audio * 32767);
    audioUnsigned = uint16(int32(audioEntero) + 32768);

    audioEsteoUnsigned = audioUnsigned;

    bitsExtraidos = zeros(1, numel(secret));
    
    for i = 1:numel(secret)
        bitsExtraidos(i) = bitget(audioEsteoUnsigned(i), 1);
    end

    codigos = jsondecode(codigos);

    claves = fieldnames(codigos);
    valores = struct2cell(codigos);
    
    claves_num = cell(1, length(claves));
    for idx = 1:length(claves)
        % disp(claves{idx});
        claves_num{idx} = str2num(claves{idx}(2:end)); 
    end
    
    % Creamos un mapa temporal con llaves de tipo texto (char)
    codigos = containers.Map(claves_num, valores);
    

    recovered_ascii_comprimido = zeros(1, length(secret));
    for i = 1:length(secret)
        recovered_ascii_comprimido(i) = descencriptacion_rsa.descifrado_rsa(secret(i), ky_pr, n);
    end
    
    recovered_ascii = descompresion_huffman.huffmanDescomprimir(recovered_ascii_comprimido, codigos, len_message)
    
    messagge_recovered = char(recovered_ascii);

    % fprintf('Descifrado: %s\n', messagge_recovered);
end