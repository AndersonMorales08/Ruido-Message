function datos = huffmanDescomprimir(bitsComprimidos, codigos, longitudOriginal)
% HUFFMANDESCOMPRIMIR Reconstruye los datos originales a partir del flujo
% de bits comprimido y el diccionario de códigos de Huffman.
%
% Aprovecha que un código de Huffman es un código de prefijo: ningún
% código es prefijo de otro, así que se puede decodificar leyendo bit a
% bit y comparando contra el diccionario, sin ambigüedad.
%
% ENTRADAS:
%   bitsComprimidos  - vector de bits (0/1), salida de huffmanComprimir
%   codigos          - containers.Map simbolo -> código (de huffmanComprimir)
%   longitudOriginal - número de símbolos que se deben recuperar
%
% SALIDA:
%   datos - vector de símbolos originales reconstruido

    % Diccionario inverso: código (string) -> símbolo
    simbolos = cell2mat(keys(codigos));
    listaCodigos = values(codigos);
    mapaInverso = containers.Map(listaCodigos, num2cell(simbolos));

    datos = zeros(1, longitudOriginal);
    cadenaBits = char(bitsComprimidos(:)' + '0'); % vector numérico -> '0'/'1'

    idx = 1;      % posición de lectura en el flujo de bits
    nDatos = 0;   % símbolos decodificados hasta ahora
    buffer = '';

    while nDatos < longitudOriginal
        buffer = [buffer cadenaBits(idx)]; %#ok<AGROW>
        idx = idx + 1;
        if isKey(mapaInverso, buffer)
            nDatos = nDatos + 1;
            datos(nDatos) = mapaInverso(buffer);
            buffer = '';
        end
    end
end