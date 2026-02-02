//Progress Bar
import {useEffect, useState} from "react";


export function useFakeProgress(isLoading: boolean) {
    const [progress, setProgress] = useState(0); //showing % of Progess bar
    useEffect(() => {
        if (isLoading == true) {
            const id = setInterval(() => {
                setProgress((prev) => {
                    const next = prev + 10;
                    if (next >= 90) {
                        clearInterval(id);
                        return 90;
                    }
                    return next;
                });
            }, 400);
        } else {
            setProgress(100);
            setTimeout(() => {
                setProgress(0);
            }, 1000);
        }
    }, [isLoading]);
}
