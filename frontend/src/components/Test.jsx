import React, { useState, useEffect } from 'react';
import axios from 'axios';

/*

Minimalny przykład logiki którą chcę uzyskać.

Problem: w strict mode komponent jest montowany dwukrotnie - useEffect wywołuje się przy pierwszym mountcie a potem drugi raz przy drugim mountcie. Następnie przychodzą odpowiedzi z serwera i dane są zapisywane do stanu dwukrotnie.

*/

function Test() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);

    const response = await axios.get('http://localhost:8000/get/');
    setData(prev => [...prev, ...response.data]);

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);
}

/*

Poniżej masz jak sobie z tym poradziłem - wprowadzenie AbortControllera. Dzięki temu unmount następujący między pierwszym a drugim mountem wywołuje przerwanie zapytania wywołanego przez pierwsze odpalenie useEffecta.

*/

function Test() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadData = async (signal) => { // dodajemy signal jako argument - gdy sygnał zostanie wywołany zostanie wywali błąd
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/get/', {signal}); // przekazujemy sygnał do axiosa
      setData(prev => [...prev, ...response.data]);
      setLoading(false);
    }
    catch (error) {
      console.error(error);

      if (error.name !== 'CanceledError' || error.code !== 'ERR_CANCELED') setLoading(false); // ustawiamy loading jako false ale poza przypadkiem gdy error wywołany jest przez AbortController. Nie chcemy by loading był ustawiony jako false w momencie gdy pierwsze zapytanie zostało przerwane a drugie nie zwróciło jeszcze danych. W takiej sytuacji dopiero po drugim zapytaniu loading ma być ustawiony na false.
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    loadData(controller.signal);

    return () => {
      controller.abort(); // cleanup wywoływany przy unmountcie - przerywamy zapytanie
    }
  }, []);
}

/*

Jaki jest teraz problem z tą logiką? W przypadku gdy zarówno pierwsze zapytanie jak i drugie zapytanie zostanie przerwane z jakiegoś powodu AbortControllerem loading nigdy nie zostanie ustawiony na false - użytkownik zostanie z wiecznym loadingiem mimo że oba zapytania się zakończyły.

*/