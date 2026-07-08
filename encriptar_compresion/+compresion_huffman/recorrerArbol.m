function codigos = recorrerArbol(todos, indice, prefijo, codigos)
    nodo = todos(indice);
    if nodo.izq == 0 && nodo.der == 0
        if isempty(prefijo)
            prefijo = '0';
        end
        codigos(nodo.simbolo) = prefijo;
    else
        codigos = compresion_huffman.recorrerArbol(todos, nodo.izq, [prefijo '0'], codigos);
        codigos = compresion_huffman.recorrerArbol(todos, nodo.der, [prefijo '1'], codigos);
    end
end