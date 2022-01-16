package main

import (
    "bytes"
    "crypto/aes"
    "crypto/cipher"
    "encoding/base64"
    "fmt"
    "io/ioutil"
    "net"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "strconv"
    "strings"
)

import "C"

func in(target string, array []string) bool {
    for _, element := range array {
        if target == element {
            return true
        }
    }
    return false
}

func getName() string {
    name, _ := os.Hostname()
    return name
}

func getIp() string {
    var ipStr string
    var IpList []string
    addrList, err := net.InterfaceAddrs()
    
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    
    for _, address := range addrList {
        // 检查ip地址判断是否回环地址
        if ipNet, ok := address.(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
            if ipNet.IP.To4() != nil {
                IpList = append(IpList, ipNet.IP.String())
            }
            
        }
    }
    
    ipStr = strings.Join(IpList, "|")
    
    return ipStr
}

func getCpuId() string {
    var cpuId string
    if runtime.GOOS == "windows" {
        cmd := exec.Command("wmic", "cpu", "get", "processorid")
        b, e := cmd.CombinedOutput()
        
        if e == nil {
            cpuId = string(b)
            cpuId = cpuId[12 : len(cpuId)-2]
            cpuId = strings.ReplaceAll(cpuId, "\n", "")
        } else {
            fmt.Printf("%v", e)
        }
    } else {
        cpuId = getLinuxCpuId()
    }
    
    // 去掉空格
    cpuId = strings.Replace(cpuId, "\t", "", -1)
    // 去除换行符
    cpuId = strings.Replace(cpuId, "\n", "", -1)
    
    return cpuId
}

func getLinuxCpuId() string {
    cmd := exec.Command("/bin/sh", "-c", `sudo dmidecode -t 4 | grep ID `)
    stdout, err := cmd.StdoutPipe()
    if err != nil {
        fmt.Println("StdoutPipe: " + err.Error())
        return ""
    }
    
    stderr, err := cmd.StderrPipe()
    if err != nil {
        fmt.Println("StderrPipe: ", err.Error())
        return ""
    }
    
    if err := cmd.Start(); err != nil {
        fmt.Println("Start: ", err.Error())
        return ""
    }
    
    bytesErr, err := ioutil.ReadAll(stderr)
    if err != nil {
        fmt.Println("ReadAll stderr: ", err.Error())
        return ""
    }
    
    if len(bytesErr) != 0 {
        fmt.Printf("stderr is not nil: %s", bytesErr)
        return ""
    }
    
    bytes, err := ioutil.ReadAll(stdout)
    if err != nil {
        fmt.Println("ReadAll stdout: ", err.Error())
        return ""
    }
    
    if err := cmd.Wait(); err != nil {
        fmt.Println("Wait: ", err.Error())
        return ""
    }
    
    return string(bytes)
    
}

func getMacAddr() string {
    var macStr string
    var macAddrList []string
    netInterfaces, err := net.Interfaces()
    if err != nil {
        fmt.Printf("fail to get net interfaces: %v", err)
        return macStr
    }
    
    for _, netInterface := range netInterfaces {
        macAddr := netInterface.HardwareAddr.String()
        if len(macAddr) == 0 {
            continue
        }
        
        macAddrList = append(macAddrList, macAddr)
    }
    macStr = strings.Join(macAddrList, "|")
    return macStr
}

//export GetDeviceInfo
func GetDeviceInfo() *C.char {
    name := getName()
    ipList := getIp()
    //cpuId := getCpuId()
    macAddr := getMacAddr()
    //res := name + "|" + ipList + "|" + cpuId + "|" + macAddr
    res := name + "|" + ipList + "|" + macAddr
    fmt.Println(res)
    return C.CString(res)
}

type AesCrypt struct {
    Key []byte
    Iv  []byte
}

func (a *AesCrypt) Encrypt(data []byte) ([]byte, error) {
    aesBlockEncrypt, err := aes.NewCipher(a.Key)
    if err != nil {
        println(err.Error())
        return nil, err
    }
    
    content := pKCS5Padding(data, aesBlockEncrypt.BlockSize())
    cipherBytes := make([]byte, len(content))
    if a.Iv == nil {
        a.Iv = a.Key
    }
    aesEncrypt := cipher.NewCBCEncrypter(aesBlockEncrypt, a.Iv)
    aesEncrypt.CryptBlocks(cipherBytes, content)
    return cipherBytes, nil
}

func (a *AesCrypt) Decrypt(src []byte) (data []byte, err error) {
    decrypted := make([]byte, len(src))
    var aesBlockDecrypt cipher.Block
    aesBlockDecrypt, err = aes.NewCipher(a.Key)
    if err != nil {
        println(err.Error())
        return nil, err
    }
    if a.Iv == nil {
        a.Iv = a.Key
    }
    aesDecrypt := cipher.NewCBCDecrypter(aesBlockDecrypt, a.Iv)
    aesDecrypt.CryptBlocks(decrypted, src)
    return pKCS5Trimming(decrypted), nil
}

func pKCS5Padding(cipherText []byte, blockSize int) []byte {
    padding := blockSize - len(cipherText)%blockSize
    padText := bytes.Repeat([]byte{byte(padding)}, padding)
    return append(cipherText, padText...)
}

func pKCS5Trimming(encrypt []byte) []byte {
    padding := encrypt[len(encrypt)-1]
    return encrypt[:len(encrypt)-int(padding)]
}

func CbcEncrypt(data string, key string) string {
    //Key := string(C.GoString(key))
    var aesCrypt = AesCrypt{
        Key: []byte(key),
        Iv:  nil,
    }
    //Data := string(C.GoString(data))
    result, err := aesCrypt.Encrypt([]byte(data))
    if err != nil {
        fmt.Println(err)
    }
    
    pass64 := base64.StdEncoding.EncodeToString(result)
    return pass64
}

func CbcDecrypt(data string, key string) string {
    //Key := string(C.GoString(key))
    var aesCrypt = AesCrypt{
        Key: []byte(key),
        Iv:  nil,
    }
    //Data := string(C.GoString(data))
    bytesPass, err := base64.StdEncoding.DecodeString(data)
    plainText, err := aesCrypt.Decrypt(bytesPass)
    if err != nil {
        fmt.Println(err)
    }
    return string(plainText)
}

//
//ctypes type 	C type 	Python type
//c_bool 	_Bool 	bool (1)
//c_char 	char 	1-character bytes object
//c_wchar 	wchar_t 	1-character string
//c_byte 	char 	int
//c_ubyte 	unsigned char 	int
//c_short 	short 	int
//c_ushort 	unsigned short 	int
//c_int 	int 	int
//c_uint 	unsigned int 	int
//c_long 	long 	int
//c_ulong 	unsigned long 	int
//c_longlong 	__int64 or long long 	int
//c_ulonglong 	unsigned __int64 or unsigned long long 	int
//c_size_t 	size_t 	int
//c_ssize_t 	ssize_t or Py_ssize_t 	int
//c_float 	float 	float
//c_double 	double 	float
//c_longdouble 	long double 	float
//c_char_p 	char * (NUL terminated) 	bytes object or None
//c_wchar_p 	wchar_t * (NUL terminated) 	string or None
//c_void_p 	void * 	int or None

//export CheckLicense
func CheckLicense(domain *C.char, port int, license *C.char) *C.char {
    defer func() {
        err := recover()
        if err != nil {
            fmt.Println(err)
        }
    }()
    
    // 域名2,4,5,3 + 端口1 + 域名2,4,5,3 + 域名1 + 端口1 + 端口2 + 域名2,4,5,3
    sDomain := C.GoString(domain)
    sLicense := C.GoString(license)
    key1 := sDomain[2:3] + sDomain[4:5] + sDomain[5:6] + sDomain[3:4]
    key2 := key1
    key3 := key1
    sPort := strconv.Itoa(port)
    
    key := key1 + sPort[0:1] + key2 + sDomain[0:1] + sPort[0:1] + sPort[1:2] + key3
    code := CbcDecrypt(sLicense, key)
    arr := strings.Split(code, "|")
    hostName := getName()
    macAddr := getMacAddr()
    //fmt.Println(macAddr)
    //fmt.Println(strings.Index(macAddr, arr[3]))
    
    if arr[0] != sDomain {
        sLicense = ""
    } else if arr[1] != sPort {
        sLicense = ""
    } else if arr[2] != hostName {
        sLicense = ""
    } else if strings.Index(macAddr, arr[3]) < 0 {
        sLicense = ""
    }
    
    return C.CString(sLicense)
}

//export GetFileType
func GetFileType(path string) int {
    lstImage := []string{".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"}
    lstDocument := []string{".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".pdf"}
    lstVideo := []string{".3gp", ".asf", ".avi", ".dat", ".dv", ".flv", ".f4v", ".gif", ".m2t", ".m3u8",
        ".m4v", ".mj2", ".mjpeg", ".mkv", ".mov",
        ".mp4", ".mpe", ".mpg", ".mpeg", ".mts", ".ogg", ".qt", ".rm", ".rmvb", ".swf", ".ts", ".vob",
        ".wmv", ".webm"}
    lstAudio := []string{".mp3", ".aac", ".ac3", ".acm", ".amr", ".ape", ".caf",
        ".flac", ".m4a", ".ra", ".wav", ".wma"}
    suffix := strings.ToLower(filepath.Ext(path))
    
    fileType := 5
    if in(suffix, lstImage) {
        fileType = 4 // 图片
    } else if in(suffix, lstDocument) {
        fileType = 1 // 文档
    } else if in(suffix, lstVideo) {
        fileType = 3 // 视频
    } else if in(suffix, lstAudio) {
        fileType = 2 // 音频
    }
    
    return fileType
}

func main() {
    //GetDeviceInfo()
    CheckLicense(C.CString("wuhan.com"), 8080, C.CString("IRtkcsDaEMadsfasdf4gUafTYRAa97yCX7O3mFILtE6MqulSlavtLXzsm2S2DpgRNsHUhPW9KmjK3FurXSnjUUmyE4QxNw=="))
    //GetFileType("aa.TXT")
    //fmt.Println(CbcDecrypt("UJTpQC17Pe3ws0jdzayzMA==", "hello,2020,2021,"))
}
