function log_sending_to_page(
    log_msg: string, 
    log_type: string = "log",
    send_page: string = "about:blank",
) {
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
    
    for (const param in get_params) {
        const exists = params.has(param)
        
        if (exists) {
            result_params[param] = params.get(param)
        }
    }

    return result_params;
}

export {log_sending_to_page, getUrlParams}