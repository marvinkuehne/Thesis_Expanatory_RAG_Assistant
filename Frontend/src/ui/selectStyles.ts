 export const getSelectStyles = (isEmpty: boolean) => ({
        // Wichtig: Container auf Inhalt dimensionieren
        container: (base: any) => ({
            ...base,
            display: "inline-block",    // verhindert 100%-Stretch im Flex-Container
            width: "fit-content",       // passt sich dem Inhalt an
            minWidth: isEmpty ? 140 : undefined, // klein starten, z.B. 140px, sonst frei
            maxWidth: 640,              // optionaler Deckel (z.B. 640px)
            flexGrow: 0,                // in Flex-Layouts nicht aufziehen
        }),
        control: (base: any) => ({
            ...base,
            width: "auto",              // nicht auf 100% ziehen
            minHeight: 40,
            backgroundColor: "#1f2937", // deine Dark-Styles
            borderColor: "#374151",
            color: "white",
        }),
        menu: (base: any) => ({
            ...base,
            backgroundColor: "#111827",
            color: "white",
            zIndex: 50,
        }),
        option: (base: any, state: any) => ({
            ...base,
            backgroundColor: state.isFocused ? "#374151" : "#111827",
            color: "white",
            cursor: "pointer",
        }),
        multiValue: (base: any) => ({
            ...base,
            backgroundColor: "#374151",
        }),
        multiValueLabel: (base: any) => ({
            ...base,
            color: "white",
        }),
        multiValueRemove: (base: any) => ({
            ...base,
            color: "white",
            ":hover": {backgroundColor: "#4b5563", color: "white"},
        }),
        // wichtige Kleinigkeiten: kein Extra-Offset, damit die Breite nicht "aufbläht"
        valueContainer: (base: any) => ({
            ...base,
            gap: 6,
            paddingRight: 8,
        }),
        input: (base: any) => ({...base, color: "white", margin: 0, padding: 0}),
        placeholder: (base: any) => ({...base, color: "#9CA3AF", margin: 0}),
    });