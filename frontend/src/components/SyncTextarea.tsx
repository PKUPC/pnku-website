// 参考 https://github.com/cm226/y-textarea
import diff from 'fast-diff';
import { useEffect, useMemo, useRef, useState } from 'react';
import getCaretCoordinates from 'textarea-caret';
import * as awarenessProtocol from 'y-protocols/awareness.js';
import * as Y from 'yjs';

import { YClient } from '@/logic/YClient';
import { cn, hslaToRgba, stringToHue } from '@/utils';
import { calcRectangleOverlap } from '@/utils';

import styles from './SyncTextArea.module.css';

export interface color {
    r: number;
    g: number;
    b: number;
}

export interface options {
    awareness: awarenessProtocol.Awareness;
    clientName?: string;
    color?: color;
    setContentValue?: (value: string) => void;
}

function getUserColor(username: string) {
    const hue = stringToHue(username);
    const rgba = hslaToRgba(hue / 360, 0.8, 0.8, 1);
    return {
        r: rgba[0],
        g: rgba[1],
        b: rgba[2],
    };
}

function createRange(element: HTMLInputElement | HTMLTextAreaElement) {
    const left = element.selectionStart as number;
    const right = element.selectionEnd as number;
    return { left, right };
}

const events = ['keyup', 'mouseup', 'touchstart', 'paste', 'cut', 'selectend'];

type CursorProps = {
    user: string;
    name: string;
    startIndex: number;
    endIndex: number;
    color: {
        r: number;
        g: number;
        b: number;
    };
};

function CursorComponent({
    name,
    color,
    startIndex,
    endIndex,
    textField,
}: CursorProps & { textField: HTMLTextAreaElement | HTMLInputElement }) {
    const [scrollPosition, setScrollPosition] = useState({ scrollTop: 0, scrollLeft: 0 });

    useEffect(() => {
        const handleScroll = () => {
            setScrollPosition({
                scrollTop: textField.scrollTop,
                scrollLeft: textField.scrollLeft,
            });
        };

        textField.addEventListener('scroll', handleScroll);
        return () => {
            textField.removeEventListener('scroll', handleScroll);
        };
    }, [textField]);

    const displayConfig = useMemo(() => {
        const textFieldFontSize = parseInt(getComputedStyle(textField).getPropertyValue('font-size'));
        let result = {
            cursorStyle: {
                top: 0,
                left: 0,
                width: 1,
                height: textFieldFontSize,
                backgroundColor: `rgba(${color.r}, ${color.g}, ${color.b}, 1)`,
                display: 'none',
            },
            nameStyle: {
                top: 0,
                left: 0,
                backgroundColor: `rgba(${color.r}, ${color.g}, ${color.b}, 1)`,
                display: 'none',
            },
        };

        if (startIndex === -1 || endIndex === -1) return result;

        const startCoordinates = getCaretCoordinates(textField, startIndex);

        const screenSpaceTop = textField.offsetTop - textField.scrollTop + startCoordinates.top;

        const screenSpaceLeft = textField.offsetLeft - textField.scrollLeft + startCoordinates.left;

        let width = 1;
        let height = 0;
        if (startIndex !== endIndex) {
            let endCoordinates = getCaretCoordinates(textField, endIndex);
            width = endCoordinates.left - startCoordinates.left;
            height = endCoordinates.top - startCoordinates.top;
            if (height !== 0) width = 1; // dont support multi line select yet
        }

        const areaScreenSpace = {
            x: textField.offsetLeft,
            y: textField.offsetTop,
            width: textField.clientWidth,
            height: textField.clientHeight,
        };

        const cursorScreenSpace = {
            x: screenSpaceLeft,
            y: screenSpaceTop,
            width: width,
            height: textFieldFontSize,
        };

        const overlap = calcRectangleOverlap(areaScreenSpace, cursorScreenSpace);
        if (!overlap) {
            return result;
        }

        result.cursorStyle.top = overlap.y;
        result.cursorStyle.left = overlap.x;
        result.cursorStyle.width = overlap.width;
        if (overlap.width === 1) {
            result.cursorStyle.backgroundColor = `rgba(${color.r}, ${color.g}, ${color.b}, 1)`;
        } else {
            result.cursorStyle.backgroundColor = `rgba(${color.r}, ${color.g}, ${color.b}, 0.4)`;
        }

        result.nameStyle.top = overlap.y + textFieldFontSize;
        result.nameStyle.left = overlap.x;

        result.cursorStyle.display = 'block';
        result.nameStyle.display = 'block';

        return result;

        // scrollPosition 需要触发新的位置计算
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [color.r, color.g, color.b, textField, startIndex, endIndex, scrollPosition]);

    return (
        <>
            <div className={styles.cursorComp} style={displayConfig.cursorStyle}></div>
            <div className={styles.nameComp} style={displayConfig.nameStyle}>
                {name}
            </div>
        </>
    );
}

function SyncCursorList({
    client,
    areaId,
    textField,
}: {
    client: YClient;
    areaId: string;
    textField: HTMLTextAreaElement | HTMLInputElement | null;
}) {
    const [cursors, setCursors] = useState<{ [key: string]: CursorProps }>({});

    useEffect(() => {
        const awarenessUpdate = (event: { removed: number[] }) => {
            if (event.removed.length != 0) {
                for (const id of event.removed) {
                    const key = id.toString();
                    if (cursors[key]) {
                        setCursors((prev) => {
                            const { [key]: _, ...rest } = prev;
                            return rest;
                        });
                    }
                }
            }

            const changes = client.provider.awareness.getStates();
            for (const [clientID, change] of changes.entries()) {
                if (clientID === client.provider.awareness.clientID) continue; // dont show local cursor
                const clientIdString = clientID.toString();

                const user = change[areaId];
                if (user === undefined) continue;

                const encodedStart = user['start'] as any;
                const encodedEnd = user['end'] as any;
                const name = user['name'] as string;
                const color = user['color'] as color;
                const selection = user['selection'] as boolean;

                if (!cursors[clientIdString] && !selection) {
                    // We don't know anything about this cursor yet,
                    // but its not selecting anything, when it does we will
                    // create it
                    continue;
                }

                let newCursorState = cursors[clientIdString] ? { ...cursors[clientIdString] } : null;
                if (!newCursorState) {
                    newCursorState = {
                        user: clientIdString,
                        name: name,
                        color: color,
                        startIndex: -1,
                        endIndex: -1,
                    };
                }
                if (!selection) {
                    newCursorState.startIndex = -1;
                    newCursorState.endIndex = -1;
                    setCursors((prev) => {
                        return {
                            ...prev,
                            [clientIdString]: newCursorState,
                        };
                    });
                    continue;
                }

                if (encodedStart === undefined || encodedEnd === undefined) continue;

                const start = Y.createAbsolutePositionFromRelativePosition(JSON.parse(encodedStart), client.doc);
                const end = Y.createAbsolutePositionFromRelativePosition(JSON.parse(encodedEnd), client.doc);

                if (start === null || end === null) {
                    newCursorState.startIndex = -1;
                    newCursorState.endIndex = -1;
                    setCursors((prev) => {
                        return {
                            ...prev,
                            [clientIdString]: newCursorState,
                        };
                    });
                    continue;
                }

                newCursorState.startIndex = start.index;
                newCursorState.endIndex = end.index;
                console.log('newCursorState', newCursorState);
                setCursors((prev) => {
                    return {
                        ...prev,
                        [clientIdString]: newCursorState,
                    };
                });
            }
        };

        client.provider.awareness.on('update', awarenessUpdate);
        return () => {
            client.provider.awareness.off('update', awarenessUpdate);
        };
    }, [areaId, client, cursors]);

    if (!textField) return <></>;

    return (
        <>
            {Object.entries(cursors).map(([userId, cursorState]) => {
                return <CursorComponent key={userId} textField={textField} {...cursorState} />;
            })}
        </>
    );
}

export function SyncTextarea({
    client,
    yText,
    className,
    username,
    userColor,
    textareaId,
}: {
    client: YClient;
    yText: Y.Text;
    textareaId: string;
    className?: string;
    username?: string;
    userColor?: { r: number; g: number; b: number };
}) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!textareaRef.current) return;
        const textField = textareaRef.current;
        textField.value = yText.toString();

        let relPosStart: Y.RelativePosition;
        let relPosEnd: Y.RelativePosition;
        let direction: typeof textField.selectionDirection;

        const onDocBeforeTransaction = () => {
            if (!textField) return;
            direction = textField.selectionDirection;
            const r = createRange(textField);
            relPosStart = Y.createRelativePositionFromTypeIndex(yText, r.left);
            relPosEnd = Y.createRelativePositionFromTypeIndex(yText, r.right);
        };
        client.doc.on('beforeTransaction', onDocBeforeTransaction);

        let textfieldChanged = false;
        const yTextObserver = (__event: Y.YTextEvent, transaction: Y.Transaction) => {
            if (transaction.local && textfieldChanged) {
                textfieldChanged = false;
                return;
            }

            textField.value = yText.toString();

            if ((textField.getRootNode() as Document).activeElement === textField) {
                const startPos = Y.createAbsolutePositionFromRelativePosition(relPosStart, client.doc);
                const endPos = Y.createAbsolutePositionFromRelativePosition(relPosEnd, client.doc);

                if (startPos !== null && endPos !== null) {
                    if (direction === null) direction = 'forward';
                    textField.setSelectionRange(startPos.index, endPos.index, direction);
                }
            }
        };
        yText.observe(yTextObserver);

        const onTextFieldInput = () => {
            textfieldChanged = true;
            const r = createRange(textField);
            let oldContent = yText.toString();
            let content = textField.value;
            let diffs = diff(oldContent, content, r.left);
            let pos = 0;
            client.doc.transact((_) => {
                for (let i = 0; i < diffs.length; i++) {
                    let d = diffs[i];
                    if (d[0] === 0) {
                        // EQUAL
                        pos += d[1].length;
                    } else if (d[0] === -1) {
                        // DELETE
                        yText.delete(pos, d[1].length);
                    } else {
                        // INSERT
                        yText.insert(pos, d[1]);
                        pos += d[1].length;
                    }
                }
            });
        };
        textField.addEventListener('input', onTextFieldInput);

        const onTextFieldChanged = () => {
            const start = textField.selectionStart as number;
            const end = textField.selectionEnd as number;

            const startRel = Y.createRelativePositionFromTypeIndex(yText, start);
            const endRel = Y.createRelativePositionFromTypeIndex(yText, end);

            client.provider.awareness.setLocalStateField(textareaId, {
                user: client.provider.awareness.clientID,
                selection: true,
                start: JSON.stringify(startRel),
                end: JSON.stringify(endRel),
                name: username || 'Anonymous',
                color: userColor || getUserColor(username || 'Anonymous'),
            });
        };
        for (const event of events) {
            textField.addEventListener(event, onTextFieldChanged);
        }

        const onFocusOut = () => {
            client.provider.awareness.setLocalStateField(textareaId, {
                user: client.provider.awareness.clientID,
                selection: false,
            });
        };
        textField.addEventListener('focusout', onFocusOut);

        return () => {
            client.doc.off('beforeTransaction', onDocBeforeTransaction);
            yText.unobserve(yTextObserver);
            textField.removeEventListener('input', onTextFieldInput);
            textField.removeEventListener('focusout', onFocusOut);
            for (const event of events) {
                textField.removeEventListener(event, onTextFieldChanged);
            }
        };
    }, [yText, client, username, userColor, textareaId]);

    return (
        <div className={cn(styles.syncTextarea, className)}>
            <textarea ref={textareaRef} id={textareaId} />
            <SyncCursorList client={client} areaId={textareaId} textField={textareaRef.current || null} />
        </div>
    );
}
