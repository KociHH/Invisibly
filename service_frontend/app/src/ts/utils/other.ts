const TIME_EXP_TOKEN = "timeExpToken"
const TIME_EXP_REPEATED = "timeExpRepeated"

function log_sending_to_page(
    log_msg: string, 
    log_type: string = "log",
    send_page: string = "about:blank",
) {
    // const url = new URL(send_page, window.location.origin);
    // url.searchParams.set('log_msg', log_msg);
    // url.searchParams.set('log_type', log_type);
    // window.location.href = url.toString();
    if (log_type == "log") {
        console.log(log_msg);
    } else if (log_type == "error") {
        console.error(log_msg);
    } else {
        console.log(`Не правильное значения аргумента log_type: ${log_type}`)
        throw new Error("Sercer error")
    }
    
    window.location.href = send_page;
}

function getUrlParams(
    get_params: string[],
    href: string = window.location.search,
) {
    const params = new window.URLSearchParams(href)
    
    type Dict = Record<string, any>
    let result_params: Dict = {}
    
    for (const param of get_params) {
        const exists = params.has(param)
        
        if (exists) {
            result_params[param] = params.get(param)
        }
    }

    return result_params;
}

function clearItemsStorage(tokens: Array<string>) {
    for (let token of tokens) {
        localStorage.removeItem(token)
    };

    console.log(`Очищенны элементы в хранилище: ${tokens}`);
    return;
}

export {
    log_sending_to_page, 
    getUrlParams, 
    clearItemsStorage,
    TIME_EXP_REPEATED,
    TIME_EXP_TOKEN
}