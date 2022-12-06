package db

import os.Path
import scala.collection.mutable.{ListBuffer, Map}
import java.sql.{Connection, DriverManager, ResultSet}
import scala.collection.mutable
import scala.io.Source
import scala.math.log

object Main extends App
{


  val tech_eng  = "Java Programming & Application Development for Google/Open Handset Alliance Mobile Phones & Internet Devices" +
                  "Python for Data Analysis: Data Wrangling with pandas, NumPy, and Jupyter" +
                  "The vast majority of Android applications are written exclusively in Java. Hence, that is what this book will spend most of its time on and will demonstrate with a seemingly infinite number of examples."+
                  "The entry point into your application was a public static void method named main() that took a String array of arguments. From there, you were responsible for doing whatever was necessary."+
                  "The system, or applications, will send out broadcasts from time to time, for everything from the battery getting low, to when the screen turns off, to when connectivity changes from WiFi to mobile data"+
                  "TXT, PDF, unprotected MOBI, PRC natively, DOCX, DOC, HTML, EPUB, TXT, RTF, JPEG, GIF, PNG, BMP through conversion, Audible audio format (AAX), Kindle Format 8 (AZW3), Kindle (AZW)"

  val tech_rus = "целостный процесс создания приложений для смартфонов и планшетов. Рассматриваются особенности мобильных операционных систем и устройств, выбор инструментов для разработки, подготовка рабочей документации в духе Agile, проектирование структуры и архитектуры решения, создание автоматизированного конвейера Continues Integration/Continues Delivery, а также мониторинг работоспособности конечного продукта на устройствах реальных пользователей. Все примеры приведены на языке C#."+
                 "Множество примеров приложений с четкими объяснениями ключевых концепций и API позволят легко разобраться в самых трудных задачах. Эта работа посвящена прикладным методам разработки приложений на Kotlin, и подойдет для всех версий Android от 5.0 (Lollipop) до 8.1 (Oreo) и выше."+
                 "Яндекс выкупил права на использование технологий книжного сервиса «Букмейт» на территории СНГ, заявили в компании."+
                 "За основу взяты открытые данные больших маркетплейсов и агрегировали их в единый каталог. Собрали датасет порядка 15 миллионов товаров с проставленными категориями."+
                 "Фундаментальный труд, который разрабатывался на протяжении нескольких десятилетий, о математике, глубоких аспектах различных алгоритмов и структур данных."+
                 "По графу процесса видно, что несколько классов были инициализированы несколько раз, если посмотреть на код, то можно увидеть, что классы Map и Filter инициализируются с различными параметрами, что не является отклонением в данном случае, а вот класс ScreenShot выбивается из общей структуры кода и вызывается несколько раз без необходимости:"


  val tech = tech_eng + " " + tech_rus

  val fiction = "как-то пошутили о моём однокласснике в школьной стенгазете. За ироничной игрой слов скрывается большая мудрость: когда ты становишься не школьником, а взрослым специалистом и вынужден вновь и вновь учиться, хочется найти волшебный эликсир запоминания и обучения. Конечно, при условии учиться не учась, потому что всё время отнимает работа и совсем немного остальная жизнь. "+
                "Получив таинственное письмо, Виктор Кэндл возвращается в город детства, где происходят мрачные и загадочные события, уходящие корнями далеко в прошлое. Старинный семейный особняк полнится заговорами. Все родственники ведут себя очень странно, а вокруг творятся необъяснимые вещи. В дом прибывают необычные гости, среди которых явно есть тот, чье присутствие все отрицают"+
                "Виолончелистке Еве напророчено стать героем, но она погибает, не успев свершить предначертанное. Только вот у одного некроманта на неё свои планы. А некромантам не может помешать такая мелочь, как смерть. Втянутая в смертельный заговор, существуя на грани между жизнью и небытием, сможет ли Ева обрести счастье? И можно ли обмануть судьбу, которая сулит, что цена победы - её гибель?"+
                "Новый роман Евгении Сафоновой, автора популярных циклов \"Тёмные игры Лиара\" и \"Сага о Форбиденах\". Первая книга дилогии, которая пронизана атмосферой музыки и смерти."+
                "Эта удивительная книга сделала ее автора одним из величайших духовных учителей человечества в XX веке. В ней философ и психолог Виктор Франкл, прошедший нацистские лагеря смерти, открыл миллионам людей всего мира путь постижения смысла жизни. Дополнительный подарок для читателя настоящего издания – пьеса «Синхронизация в Биркенвальде», где выдающийся ученый раскрывает свою философию художественными средствами."+
                //"Психолог Михаил Лабковский абсолютно уверен: вырастить из ребенка не «удобного» взрослого, а психологически здорового человека, самостоятельного и счастливого. А растить детей счастливыми, если вы сами наслаждаться жизнью пока не научились – невозможно. Поэтому в этой книге сперва «надеваем кислородную маску» на родителей"+
                "Ты что, маньяк? Этот вопрос врач-психиатр Гуревич все время слышит ото всех вокруг. Не умеет он сидеть спокойно, не высовываться, не лезть «не в свое дело», вечно норовит кого-то спасти, кому-то помочь, поставить всех на уши – за что и получает с незавидной регулярностью. И ничему-то его жизнь не учит, ну точно маньяк какой-то! В жизни и практике психиатра Гуревича – множество смешных и драматических, трогательных и нелепых, грустных и гомерически смешных историй. И раз за разом он доказывает: в любой, самой тяжелой и мрачной ситуации можно вести себя по-человечески. И все-таки, может, не так уж плохо быть маньяком, если это значит, что ты остаешься человеком?"+
                "Ночь, улица, фонарь, аптека, Бессмысленный и тусклый свет. Живи еще хоть четверть века — Всё будет так. Исхода нет. Умрешь — начнешь опять сначала И повторится всё, как встарь: Ночь, ледяная рябь канала, Аптека, улица, фонарь."+
                "будущее из руин и обломков прошлого и создать великую галактическую цивилизацию, избавленную от войн, розни, лжи и секретов. Не пропустите невероятно захватывающее завершение величайший космооперы десятилетия, награжденной премией «Хьюго»"

  implicit class StringOperations(val s: String)
  {
    def deleteSymbols = s.replaceAll("[!,«»—.:?()\"/]", "").toLowerCase

    def getWords = s.deleteSymbols.split(" ")

    def getUniqWords = s.getWords.distinct

    def getWordCountList(masterText: String) = for {word <- s.getUniqWords

                                                                         } yield (word, masterText.getWords.count(_ == word))

  }


  def getConnection() =
  {
    val file = os.read(Path("C:\\my_files\\dz\\_univer\\_маг_Методы_извлечения_информации_из_сетевых_источников\\project\\privates.json"))
    val info = ujson.read(file)

    classOf[org.postgresql.Driver]
    val con_st = s"jdbc:postgresql://${info("bd_host").str}:5432/Papers?user=${info("bd_login").str}&password=${info("bd_psw").str}"
    DriverManager.getConnection(con_st)
  }

  def query(sql: String): Array[(Int, String)] =
  {
    val conn = getConnection
    var texts = Array.empty[(Int, String)]

    try
    {
      val stmt = conn.prepareStatement(sql)//conn.createStatement()
      val rs = stmt.executeQuery()


      while (rs.next())
      { texts = texts :+ ( rs.getInt("id"), rs.getString("paper_text"))
      }

    }
    finally
    { conn.close() }

    texts

  }


  def updateTable(x:(Int, String)): Unit =
  {

    val conn = getConnection
    val sql = "Update papers set type = ? where id = ?;"

    try
    { val stmt = conn.prepareStatement(sql)
      stmt.setString(1, x._2)
      stmt.setInt(2, x._1)

      stmt.executeUpdate()
    }
    finally
    {
      conn.close()
    }

  }

  def naiveBayes(text: String,  typeClass: Int = 1): Double =
  {
    // если typeClass = 1 - рассматриваем tech, иначе fiction

    val classes = collection.mutable.Map("tech"-> 2, "fiction" -> 1)
    val uniqWords = (tech + " " + fiction).getUniqWords.length

    var first, second = 0.0

    if (typeClass == 1)
    {
      val techWordsAll = tech.getWords.length
      first = log(classes("tech")/(classes("tech")+ classes("fiction")).toDouble)
      val wordCount = text.getWordCountList(tech)
      second = wordCount.map(x => log((1+x._2)/(uniqWords+techWordsAll).toDouble) ).sum

    }
    else
    {
      val fictWordsAll = fiction.getWords.length
      first = log(classes("fiction")/(classes("tech")+ classes("fiction")).toDouble)
      val wordCount = text.getWordCountList(fiction)//dataset(0)._2
      second = wordCount.map(x => log((1+x._2)/(uniqWords+fictWordsAll).toDouble) ).sum
    }

    first + second
  }

  def checkBayes
  {
    val sql = "Select id, paper_text from papers where type is Null"
    val dataset = query(sql)
    val dataset1 = dataset.map(x => (x._1, if (naiveBayes(x._2)>naiveBayes(x._2, 0))  "Техническая" else "Художественная"))
    dataset1.foreach(println(_))
    dataset1.foreach(updateTable(_))
  }

  checkBayes



}