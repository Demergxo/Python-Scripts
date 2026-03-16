

def change_location(sku_item, location):
    """confirmar cambios de ubicacion"""
    print("change location")
    loc_url = driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/div[3]/div[1]/div[2]/span").text
    sku_url = driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/div[3]/div[2]/div[2]/span").text
    print("location url: " + loc_url + " location: " + location)
    #print("sku url: "+ sku_url + " sku: " + sku_item)
    
    
    if location == loc_url:
        if sku_item == sku_url:
            driver.find_element("xpath", "//*[@id='skuConf']").send_keys(sku_item)
            time.sleep(3)
            driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/form/div[2]/div[1]/button/span[1]").click()
    time.sleep(5)        
            

  

def is_number(lpn):
    """saber si es un numero o no"""
    if lpn == None:
        lpn = ""  
    
    try:
        int(lpn)
    except ValueError:
        return False
    return True

   
def test_check(first_sku, row_limit, check_col):
    
    result = 0
    
    for i in range(first_sku, row_limit + 1):
        
        check = sheet_obj.cell(row =i, column = check_col).value
        
        if check == "Y":
            result += 1
    
    return result


#
def fill_sku_list(first_sku_row, article_col, row_limit):
    """Cargar una lista con todos los Sku"""
    fill_list= []
    for name in range(first_sku_row, row_limit+1):
        fill_list.append(sheet_obj.cell(row=name, column=article_col).value)
        fill_list = list(dict.fromkeys(fill_list))
    #print(*fill_list, sep=", ")
    return fill_list

#
def list_sku_terminated(sku):
    """añadir sku por terminados"""
    sku_terminated = []
    sku_terminated.append(sku)
    #print(sku_terminated)
    return sku_terminated

#
def comparar_listas(fill_list, sku_terminated, sku, location):
    """Comparar listas"""
    if (set(fill_list)==set(sku_terminated)):
        print("Proceso Completado")
        return True
    else:
        #print("Continuamos...")
        siguiente_conteo(location, sku)
        return False

def siguiente_conteo(location, sku): #REVISAR FUNCION
    """tocar CC1, From LOC y SKU e introducir el codigo"""

    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[1]/div/mat-button-toggle-group/mat-button-toggle[1]/button/span/span").click()
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[2]/div/mat-button-toggle[1]/button/span/span").click()
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[2]/div/mat-button-toggle[3]/button/span/span").click()

    time.sleep(5)

    var_loc = location
    var_sku = sku

    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[3]/div/div[1]/mat-form-field/div/div[1]/div/mat-select/div/div[1]").click()
    driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/div/mat-option[2]/span").click()

    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[3]/div/div[2]/mat-form-field/div/div[1]/div/input").send_keys(var_sku)
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[3]/div/div[3]/mat-form-field/div/div[1]/div/input").send_keys(var_loc)
    time.sleep(5)
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/div[2]/form/div[4]/button/span[1]").click()

    time.sleep(10)
    
    #entrar en menu de conteo por localización 

    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/form/div[1]/div/mat-form-field/div/div[1]/div/input").send_keys(var_loc)
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/form/div[1]/div[2]/mat-form-field/div/div[1]/div/input").send_keys(var_sku)
    time.sleep(3)
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-confirmation/div/div/form/div[2]/div[1]/button").click()

    time.sleep(3)
    driver.find_element("xpath", "/html/body/app-root/xpo-shell/xpo-tab-drawer/mat-drawer-container/mat-drawer-content/xpo-tab-drawer-content/app-cycle-count/div/app-cycle-count-lot-execution/div/div/form/div[4]/div[2]/button/span[1]").click()

def fill_key_list(first_sku_row, row_limit, sku_col, location_col, lpn_col, batch_col, qty_col):
    """Creamos una funcion que añada una clave unica y lo corresponda a un valor"""
    key_list={}
                
    for i in range(first_sku_row, row_limit + 1):
        sku = sheet_obj.cell(row = i, column = sku_col).value
        loc = sheet_obj.cell(row = i, column = location_col).value
        lpn = sheet_obj.cell(row = i, column = lpn_col).value
        batch = sheet_obj.cell(row =i, column = batch_col).value
        value = sheet_obj.cell(row = i, column = qty_col).value

        if lpn == None:
            lpn_check = ""
                    
        if (not is_number(lpn)) or lpn == None:
            lpn_check = lpn
                        #print(lpn_check)
                        
        if is_number(lpn):
            lpn_check = str(lpn).zfill(10)
            #print(lpn_check)
                    
        if lpn_check == None:
            lpn_check = ""
                        
        if batch == None:
            batch = ""

        #print(("EXCEL -> SKU: {} Len: {}").format(sku, len(sku)))
        #print(("EXCEL -> LOC: {} Len: {}").format(loc, len(loc)))
        #print(("EXCEL -> LPN: {} Len: {}").format(lpn_check, len(lpn_check)))
        #print(("EXCEL -> Batch: {} Len: {}").format(batch, len(batch)))
        #print(("EXCEL -> QTY: {} \n").format(value))
         #key_loc+key_sku+key_batch+key_lot+key_lpn

        keys_fan = str(loc+sku+batch+lpn_check)
        key_list.setdefault(keys_fan, value)
    
    return key_list

def busqueda_binaria_recursiva(lista, key, left, right):
    """Funcion para buscar un elemento en una lista ordenada mediante busqueda binaria"""
    if left > right:
        return -1
    middlepos = (left + right) // 2
    middle = lista[middlepos]
    if middle == key:
        print(("MIDLE=KEY BBINARIA: {}").format(middlepos))
        return middlepos
    if key < middle:
        print(("KEY<MIDDLE MEDIA BBINARIA: {}").format(middlepos))
        return (middlepos - 1)
    else:
        print(("KEY > MIDDLE MEDIA BBINARIA: {}").format(middlepos))
        return(middlepos + 1)

def pasar_sku(lista, first_sku_row, row_limit,check_col):
    """para pasar de un sku finalizado a otro que todavía no hayamos realizado"""
    
    for i in range(first_sku_row, row_limit+1):
        check = sheet_obj.cell(row = i, column = check_col).value
        
        print(("CHECK: {} I: {}").format(check, (i-1)))
        if check != "Y":
            return lista[i-2]
         
        else:
            pass